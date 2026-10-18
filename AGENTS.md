# AGENTS.md — working on this repository

Read [README.md](README.md) first (method, setup, results). This file holds the rules that keep the
video, the experiments and the documentation consistent.

## Commands

```bash
uv sync                                   # Python 3.12 venv in .venv (torch from the CUDA 12.8 index)
uv run pytest -m "not gpu and not network"  # fast tests
uv run pytest                              # + GPT-2 steering tests (GPU) + verbatim quote check (internet)
uv run steering-explainer --phases verify_sources
uv run steering-explainer --phases render --chapters ch07 --quality l   # preview one chapter
uv run steering-explainer --phases inspect                              # contact sheets -> outputs/check/
uv run steering-explainer --phases render assemble                      # final video (RENDER_QUALITY=f)
```

## Single sources of truth (never duplicate their content elsewhere)

| What | Where | Consumers |
|---|---|---|
| Narration | `data/script.yaml` | scenes (`self.say(beat)`), subtitles, tests |
| Term definitions + defining chapter | `data/glossary.yaml` | `tests/test_script.py`, `docs/glossary.md` (generated) |
| Citations + verbatim quotes | `data/sources.yaml` | quote cards, footers, `docs/sources.md` (generated), `outputs/description.md` |
| Real model numbers | `data/practical_example.json` (phase `practical_example`) | chapters 00-08, narration placeholders |
| Study results | `data/study/summary.json`, `exp02_summary.json` | chapter 09, reports, paper |
| Settings | `.env.example` (defaults) / `.env` (overrides) | `config.load_settings()` only |

## Rules

* **No hand-typed numbers on screen or in narration.** Toy numbers come from `video/toy.py`, real ones
  from the JSON files via `video/narration_values.py`.
* **Define before use.** Adding a term to the narration → add it to `data/glossary.yaml` with the chapter
  that defines it; `tests/test_script.py` fails if an earlier chapter mentions it.
* **Quotes are verbatim.** Add them to `data/sources.yaml`, run `uv run pytest -m network`; quotes from
  sources not licensed CC BY 4.0 must stay ≤ 15 words (tested).
* **Pre-register before data.** A new experiment gets a `reports/expNN_preregistration.md` committed
  *before* its first generation run; anything not in it is reported as post-hoc.
* **Sync visuals to speech** with `<bookmark mark='x'/>` in the script and `self.wait_until_bookmark("x")`
  in the scene (edge-tts word timings make this exact).
* **Inspect renders.** After changing a scene, render at `--quality l`, run `--phases inspect`, and look at
  the contact sheet for overlaps, clipped text and footer collisions.
* Logs: every run writes `logs/run_<timestamp>.log` with full prompts, completions and narration.
* Steering hook changes must keep `tests/test_steering.py` green (identity at α = 0, exact α·v at the
  front positions, cached = uncached generation).
* Git: feature branch → PR → merge; never commit `.env`, `.cache/`, `media/` or MP4 files (the video is a
  GitHub Release asset).
