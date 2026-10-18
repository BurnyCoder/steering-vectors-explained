"""render.py — render every chapter with Manim, then assemble one MP4 with chapters, subtitles and a description.

Global context: phase `render` runs `python -m manim -q<quality>` once per scene file (each chapter is
its own Scene, so a failing chapter can be re-rendered alone); phase `assemble` concatenates the
chapter MP4s losslessly with ffmpeg's concat demuxer, embeds chapter markers via an FFMETADATA file,
merges the per-chapter .srt subtitles (shifted by each chapter's start time) and writes
outputs/description.md (chapter timestamps + every source).
Docs: ffmpeg concat demuxer (https://trac.ffmpeg.org/wiki/Concatenate), FFMETADATA chapters
(https://ffmpeg.org/ffmpeg-formats.html#Metadata-1), srt library (https://srt.readthedocs.io).
"""

import os
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import srt

from steering_explainer.config import Settings
from steering_explainer.log import get_logger
from steering_explainer.video.widgets import registry, script

log = get_logger(__name__)
QUALITY_DIR = {"l": "480p15", "m": "720p30", "h": "1080p60", "k": "2160p60"}  # Manim's output folder names
SCENES = Path(__file__).parent / "scenes"


def chapter_files() -> list[Path]:
    return sorted(SCENES.glob("ch[0-9][0-9]_*.py"))


def _class_name(path: Path) -> str:
    return "Ch" + path.stem[2:4]  # ch07_build.py -> Ch07


def _run(cmd: list[str]) -> None:
    """Run a command, streaming every output line into the run log."""
    log.info("$ %s", " ".join(cmd))
    env = {**os.environ, "COLUMNS": "250", "PYTHONIOENCODING": "utf-8"}  # wide rich console: unwrapped Manim log lines
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                            errors="replace", env=env)
    for line in proc.stdout:
        if line.strip():
            log.info("  %s", line.rstrip())
    if proc.wait() != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(cmd)}")


def chapter_video(s: Settings, path: Path) -> Path:
    return s.root / "media" / "videos" / path.stem / QUALITY_DIR[s.render_quality] / f"{_class_name(path)}.mp4"


def render_chapters(s: Settings, only: list[str] | None = None) -> list[Path]:
    """Render all (or the `only` ch-ids) chapters; returns the chapter MP4 paths in order."""
    outs = []
    for path in chapter_files():
        if not only or path.stem[:4] in only:
            _run([sys.executable, "-m", "manim", f"-q{s.render_quality}", "--media_dir", str(s.root / "media"),
                  str(path), _class_name(path)])
        outs.append(chapter_video(s, path))
    return outs


def contact_sheets(s: Settings, every_s: float = 3.0) -> list[Path]:
    """One PNG grid of frames per rendered chapter (outputs/check/), for visual QA of overlaps/overflow."""
    out_dir = s.outputs_dir / "check"
    out_dir.mkdir(parents=True, exist_ok=True)
    sheets = []
    for f in chapter_files():
        mp4 = chapter_video(s, f)
        if not mp4.exists():
            continue
        n = max(1, int(_duration(mp4) // every_s) + 1)  # frames in the grid
        cols = 5
        png = out_dir / f"{f.stem}.png"
        _run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4), "-vf",
              f"fps=1/{every_s},scale=480:-1,tile={cols}x{-(-n // cols)}:padding=4:color=white", "-frames:v", "1", str(png)])
        sheets.append(png)
    return sheets


def _duration(mp4: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def _stamp(sec: float) -> str:
    m, s_ = divmod(int(round(sec)), 60)
    return f"{m:02d}:{s_:02d}"


def assemble(s: Settings) -> Path:
    """Concatenate chapter videos -> outputs/steering_vectors_explained.mp4 (+ .srt, description.md)."""
    files = chapter_files()
    mp4s = [chapter_video(s, f) for f in files]
    missing = [m for m in mp4s if not m.exists()]
    if missing:
        raise FileNotFoundError(f"render these chapters first: {missing}")
    out_dir = s.outputs_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    starts, t = [], 0.0
    for m in mp4s:
        starts.append(t)
        t += _duration(m)
    titles = [script()[f.stem[:4]]["title"] for f in files]

    lst = out_dir / "concat.txt"  # concat demuxer input list
    lst.write_text("".join(f"file '{m.as_posix()}'\n" for m in mp4s), encoding="utf-8")
    meta = out_dir / "chapters.ffmeta"  # chapter markers in milliseconds
    meta.write_text(";FFMETADATA1\ntitle=Steering vectors, from scratch\nartist=Libor Burian\n" + "".join(
        f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(a * 1000)}\nEND={int(b * 1000)}\ntitle={ti}\n"
        for a, b, ti in zip(starts, starts[1:] + [t], titles)), encoding="utf-8")
    video = out_dir / "steering_vectors_explained.mp4"
    _run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(meta),
          "-map_metadata", "1", "-map_chapters", "1", "-c", "copy", str(video)])

    subs = []  # merged subtitles, shifted by chapter start
    for m, a in zip(mp4s, starts):
        srt_path = m.with_suffix(".srt")
        if srt_path.exists():
            for sub in srt.parse(srt_path.read_text(encoding="utf-8")):
                sub.start += timedelta(seconds=a)
                sub.end += timedelta(seconds=a)
                subs.append(sub)
    (out_dir / "steering_vectors_explained.srt").write_text(srt.compose(subs), encoding="utf-8")

    reg = registry()
    desc = ["# Steering vectors, from scratch — video description", "",
            "Narrated explainer of LLM steering vectors (activation addition), every term defined from scratch,",
            "grounded in a real, pre-registered GPT-2-XL experiment. Author: Libor Burian (independent researcher).",
            "Code, data and logs: https://github.com/BurnyCoder/steering-vectors-explained", "", "## Chapters", ""]
    desc += [f"{_stamp(a)} {ti}" for a, ti in zip(starts, titles)]
    desc += ["", f"Total length: {_stamp(t)}", "", "## Sources", ""]
    desc += [f"- {src.citation} {src.url}" for src in reg.values()]
    (out_dir / "description.md").write_text("\n".join(desc) + "\n", encoding="utf-8")
    log.info("Assembled %s (%s) with %d chapters and %d subtitles", video, _stamp(t), len(files), len(subs))
    return video
