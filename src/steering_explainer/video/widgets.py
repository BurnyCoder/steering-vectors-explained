"""widgets.py — the ChapterScene base class and reusable on-screen components.

Global context: every chapter (video/scenes/chXX_*.py) subclasses ChapterScene, which
  * sets the dark background and the edge-tts narration service (tts_edge.EdgeTTSService),
  * reads that chapter's narration beats from data/script.yaml (`self.say(beat_id)`), filling
    {placeholders} with numbers computed from data/*.json (so spoken numbers are never typed by hand),
  * draws a citation footer (`self.cite`) for every slide that makes a sourced claim.
Components (quote cards, definition cards, vector labels, symbol tables) are plain functions that
return Manim mobjects. Manim docs: https://docs.manim.community/en/stable/reference.html;
manim-voiceover usage: https://voiceover.manim.community/en/stable/quickstart.html.
"""

import json
import re
import textwrap
from functools import lru_cache

from manim import (BOLD, DOWN, ITALIC, LEFT, RIGHT, UP, Arrow, FadeIn, FadeOut, Line, MathTex, NumberPlane,
                   Rectangle, RoundedRectangle, Text, VGroup)
from manim_voiceover import VoiceoverScene
import yaml

from steering_explainer import sources
from steering_explainer.config import ROOT, load_settings
from steering_explainer.log import get_logger
from steering_explainer.video import theme as T
from steering_explainer.video.tts_edge import EdgeTTSService

log = get_logger(__name__)


@lru_cache
def script() -> dict:
    """{chapter_id: {"title": str, "beats": {beat_id: text}}} from data/script.yaml."""
    raw = yaml.safe_load((ROOT / "data" / "script.yaml").read_text(encoding="utf-8"))
    return {c["id"]: {"title": c["title"], "beats": {b["id"]: " ".join(b["text"].split()) for b in c["beats"]}}
            for c in raw["chapters"]}


@lru_cache
def registry() -> dict:
    return sources.load_sources(ROOT / "data" / "sources.yaml")


@lru_cache
def example() -> dict:
    """Real GPT-2-XL numbers (steering/example.py)."""
    return json.loads((ROOT / "data" / "practical_example.json").read_text(encoding="utf-8"))


@lru_cache
def study() -> dict:
    """Pre-registered study summary (study/analyze.py); empty until the study has run."""
    path = ROOT / "data" / "study" / "summary.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def narration_values() -> dict:
    """Placeholder values for script.yaml, computed from the JSON results (see docs/storyboard.md)."""
    from steering_explainer.video.narration_values import compute  # kept separate: pure data -> strings
    return compute(example(), study())


class ChapterScene(VoiceoverScene):
    """Base scene: background, narration service, script beats, footer citations."""

    CHAPTER = "ch00"  # overridden by each chapter

    def setup(self):
        s = load_settings()  # PATH (MiKTeX) + voice settings from .env
        self.camera.background_color = T.BG
        self.set_speech_service(EdgeTTSService(voice=s.tts_voice, rate=s.tts_rate))
        self.beats = script()[self.CHAPTER]["beats"]
        self.values = narration_values()
        self.footer = None

    def say(self, beat_id: str):
        """Context manager speaking one beat; animations inside it play during the narration."""
        text = self.beats[beat_id].format(**self.values)  # fill {placeholders} with real numbers
        log.info("[%s/%s] NARRATION: %s", self.CHAPTER, beat_id, text)
        return self.voiceover(text=text)

    def cite(self, *source_ids: str, extra: str = ""):
        """Replace the bottom-left footer with the short citations of `source_ids`."""
        reg = registry()
        label = "Source: " + "; ".join(reg[i].short for i in source_ids) + (f"; {extra}" if extra else "")
        new = Text(label, font=T.FONT, font_size=T.SIZE_CITE, color=T.MUTED).to_corner(DOWN + LEFT, buff=0.25)
        anims = [FadeIn(new)] + ([FadeOut(self.footer)] if self.footer else [])
        self.footer = new
        self.play(*anims, run_time=0.4)

    def uncite(self):
        if self.footer:
            self.play(FadeOut(self.footer), run_time=0.3)
            self.footer = None

    def clear_stage(self, run_time: float = 0.6):
        """Fade out everything except the footer."""
        mobs = [m for m in self.mobjects if m is not self.footer]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)

    def chapter_title(self) -> Text:
        """Top-left heading with the chapter title (stays during the chapter)."""
        heading = Text(script()[self.CHAPTER]["title"], font=T.FONT, font_size=T.SIZE_TITLE, color=T.FG, weight=BOLD)
        return heading.to_edge(UP, buff=0.35)


def text(s: str, size: int = T.SIZE_BODY, color: str = T.FG, width: int = 0, **kw) -> Text:
    """Text in the house font; `width` > 0 wraps at that many characters."""
    return Text(textwrap.fill(s, width) if width else s, font=T.FONT, font_size=size, color=color, line_spacing=0.8, **kw)


def quote_card(quote_id: str, width: int = 58, size: int = 26) -> VGroup:
    """Verbatim quote (italic, wrapped) + attribution line; text comes from data/sources.yaml."""
    q, src = sources.get_quote(registry(), quote_id)
    shown = re.sub(r'"([^"]*)"', r"‘\1’", q.text)  # quotes inside a quotation become single quotes (typographic nesting)
    body = text("“" + shown + "”", size=size, width=width, slant=ITALIC)
    attribution = text(f"— {src.short}, {q.location}", size=min(size, T.SIZE_SMALL) - 4, color=T.FG2, width=int(width * 1.2))
    group = VGroup(body, attribution).arrange(DOWN, aligned_edge=RIGHT, buff=0.2)
    bar = Line(group.get_corner(UP + LEFT), group.get_corner(DOWN + LEFT), color=T.STEER, stroke_width=4).shift(0.2 * LEFT)
    card = VGroup(bar, group)
    return card.scale_to_fit_width(12.6) if card.width > 12.6 else card  # never wider than the frame


def definition_card(term: str, sentence: str, math: str = "", width: int = 52) -> VGroup:
    """Boxed definition: coloured term, optional set-membership formula, one explanatory sentence."""
    head = text(term, size=T.SIZE_BODY, color=T.TERM, weight=BOLD)
    parts = [head] + ([MathTex(math, color=T.FG, font_size=40)] if math else []) + [text(sentence, T.SIZE_SMALL, T.FG2, width)]
    body = VGroup(*parts).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    box = RoundedRectangle(corner_radius=0.15, width=body.width + 0.5, height=body.height + 0.4,
                           stroke_color=T.MUTED, stroke_width=1.5).move_to(body)
    return VGroup(box, body)


def num(x, nd: int = 3) -> str:
    """Display a number: integers without decimals, others rounded to `nd` decimals (Fractions included)."""
    f = float(x)
    return str(int(f)) if f.is_integer() else f"{round(f, nd):g}"


def tup(values, nd: int = 3) -> str:
    """LaTeX source of a tuple of computed numbers, e.g. "(6,-2)"."""
    return "(" + ",".join(num(v, nd) for v in values) + ")"


def vec_tex(values, color: str = T.VEC, size: int = 40, nd: int = 3) -> MathTex:
    """A vector written as a tuple, e.g. (2, 1)."""
    return MathTex(r"\left(" + ",\\ ".join(num(v, nd) for v in values) + r"\right)", color=color, font_size=size)


def symbol_row(symbol: str, membership: str, meaning: str, color: str = T.FG) -> VGroup:
    """One recap row: symbol | what set it belongs to | one-sentence meaning."""
    return VGroup(MathTex(symbol, color=color, font_size=34), MathTex(membership, color=T.SET, font_size=30),
                  text(meaning, T.SIZE_SMALL, T.FG2))


def bullet_list(items: list[str], size: int = T.SIZE_SMALL, width: int = 60) -> VGroup:
    return VGroup(*[text("• " + it, size, T.FG, width) for it in items]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)


def plane(x_range=(-3, 7), y_range=(-3, 4), unit: float = 0.55) -> NumberPlane:
    """A small coordinate grid (1 unit per grid line) for 2-D toy vectors."""
    return NumberPlane(x_range=[x_range[0], x_range[1], 1], y_range=[y_range[0], y_range[1], 1],
                       x_length=(x_range[1] - x_range[0]) * unit, y_length=(y_range[1] - y_range[0]) * unit,
                       background_line_style={"stroke_color": T.MUTED, "stroke_width": 1, "stroke_opacity": 0.35},
                       axis_config={"stroke_color": T.FG2, "stroke_width": 2})


def arrow(pl: NumberPlane, v, color: str = T.VEC, start=(0, 0)) -> Arrow:
    """Arrow for vector v drawn from `start` on plane `pl` (tip-to-tail when start ≠ origin)."""
    s = [float(x) for x in start]
    e = [s[0] + float(v[0]), s[1] + float(v[1])]
    return Arrow(pl.c2p(*s), pl.c2p(*e), buff=0, color=color, stroke_width=5, max_tip_length_to_length_ratio=0.18)


def tip_label(arr: Arrow, tex: str, color: str, direction=UP, size: int = 34) -> MathTex:
    """Small MathTex label next to an arrow's tip (e.g. 'a+b')."""
    return MathTex(tex, color=color, font_size=size).next_to(arr.get_end(), direction, buff=0.08)


class EqColumn:
    """Stack equations top-down in a left-aligned column, shrinking any that would overflow `width`."""

    def __init__(self, left: float = 0.9, top: float = 2.4, width: float = 6.2, buff: float = 0.32):
        self.left, self.y, self.width, self.buff = left, top, width, buff

    def place(self, m):
        if m.width > self.width:
            m.scale_to_fit_width(self.width)  # never run off the frame
        m.move_to([self.left + m.width / 2, self.y - m.height / 2, 0])
        self.y -= m.height + self.buff
        return m


def show_token(tok: str) -> str:
    """Make whitespace inside a GPT-2 token visible: spaces as '·' ('·hate', '·'), newlines as '↵'."""
    return tok.replace(" ", "·").replace("\n", "↵")


def token_row(tokens: list[str], color: str = T.FG, size: int = 32, buff: float = 0.3) -> VGroup:
    """Tokens as boxed chips in a row (min chip width keeps one-letter tokens readable)."""
    chips = []
    for t in tokens:
        label = text(show_token(t), size, color)
        box = RoundedRectangle(corner_radius=0.1, width=max(label.width + 0.35, 0.9), height=0.75,
                               stroke_color=color, stroke_width=1.5).move_to(label)
        chips.append(VGroup(box, label))
    return VGroup(*chips).arrange(RIGHT, buff=buff)


def prob_bars(labels: list[str], probs: list[float], color: str = T.VEC, max_width: float = 4.0,
              size: int = 28, tokens: bool = True, signed: bool = False) -> VGroup:
    """Horizontal probability bars: label | bar (length ∝ p, axis 0..1) | value."""
    rows = []
    for lab, p in zip(labels, probs):
        name = text(show_token(lab) if tokens else lab, size, T.FG)
        bar = Rectangle(width=max(abs(float(p)) * max_width, 0.02), height=0.34, fill_color=color, fill_opacity=0.9, stroke_width=0)
        val = text(f"{float(p):+.3f}" if signed else f"{float(p):.3f}", size, T.FG2)
        rows.append(VGroup(name, bar, val))
    w = max(r[0].width for r in rows)
    for i, r in enumerate(rows):  # align label column, bars start at the same x
        r[0].move_to([0, -i * 0.55, 0]).align_to([-w, 0, 0], LEFT)
        r[1].next_to([0.2, -i * 0.55, 0], RIGHT, buff=0)
        r[2].next_to(r[1], RIGHT, buff=0.15)
    return VGroup(*rows)


__all__ = ["ChapterScene", "text", "quote_card", "definition_card", "vec_tex", "symbol_row", "bullet_list",
           "example", "study", "registry", "RIGHT", "LEFT"]
