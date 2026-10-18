"""ch09_study.py — our two pre-registered experiments: dose-response with a random-direction control.

Global context: shows the design (reports/exp01_preregistration.md, exp02_preregistration.md), the
control idea, the metric, and the measured result figure of the powered replication (study/plots.py,
dark theme) with numbers from data/study/summary.json and exp02_summary.json — narrated through
narration_values.py, whatever the verdicts are.
"""

import math

import numpy as np
from PIL import Image

from manim import (DOWN, LEFT, RIGHT, UP, Circle, Create, DashedVMobject, FadeIn, FadeOut, GrowArrow, ImageMobject,
                   MathTex, Rectangle, VGroup, Write)

from steering_explainer.config import ROOT
from steering_explainer.video import theme as T
from steering_explainer.video.widgets import ChapterScene, arrow, plane, study, text

RAND = "#d95926"  # random-control colour (same as the study figure, plots.THEMES["dark"]["rand"])
STEER_FIG = "#3987e5"  # steered colour in the study figure (plots.THEMES["dark"]["steer"]), reused so both views match


def _ci(m: float, lo: float, hi: float) -> str:
    return rf"{m:+.3f}\ \ [{lo:+.3f},\ {hi:+.3f}]"


class Ch09(ChapterScene):
    CHAPTER = "ch09"

    def construct(self):
        st1, st2 = study(), study("exp02_summary")
        head = self.chapter_title()
        self.play(Write(head))

        with self.say("question"):
            self.cite("maas2011imdb", extra="IMDb review openings, first 8 words; reports/exp0*_preregistration.md")
            alphas = ",\\ ".join(f"{a:g}" for a in sorted({float(k.split('_')[1]) for k in st2["means"]["p_pos"] if k.startswith("steer_")}))
            design = VGroup(
                MathTex(rf"\text{{run 1: }}{st1['n_prompts']}\ \text{{prompts}}\qquad \text{{run 2: }}{st2['n_prompts']}\ \text{{new prompts}}", font_size=40),
                MathTex(rf"\times\ \alpha\in\{{{alphas}\}}\ \times\ {len(st2['seeds'])}\ \text{{samples each}}", font_size=40),
            ).arrange(DOWN, buff=0.25).shift(UP * 1.7)
            ex = VGroup(*[text(f"“{e['prompt']} …”", T.SIZE_SMALL, T.FG2) for e in st2["examples"]]).arrange(DOWN, aligned_edge=LEFT).shift(DOWN * 0.2)
            pre = text("plans written and committed before any data were generated", T.SIZE_SMALL, T.PLUS).shift(DOWN * 2.1)
            self.play(Write(design)); self.play(FadeIn(ex, lag_ratio=0.3)); self.play(FadeIn(pre))
        self.clear_stage(); self.add(head)

        with self.say("control"):
            pl = plane((-3, 3), (-3, 3), 0.75).shift(LEFT * 3 + DOWN * 0.3)
            v = arrow(pl, (2, 0), STEER_FIG)
            angles = [0.9, 2.0, 2.9, 4.1, 5.2]  # fixed illustrative angles for 5 random directions
            rnd = [arrow(pl, (2 * math.cos(a), 2 * math.sin(a)), RAND) for a in angles]
            ring = DashedVMobject(Circle(radius=2 * 0.75, color=T.MUTED).move_to(pl.c2p(0, 0)), num_dashes=40)
            cap = VGroup(text("steering vector v", T.SIZE_SMALL, STEER_FIG), text("5 random directions, same norm ‖v‖", T.SIZE_SMALL, RAND),
                         text("same prompts, same random choices", T.SIZE_SMALL, T.FG2)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).shift(RIGHT * 3.2)
            self.play(Create(pl), GrowArrow(v), FadeIn(cap[0]))
            self.play(Create(ring), *[GrowArrow(r) for r in rnd], FadeIn(cap[1]))
            self.play(FadeIn(cap[2]))
        self.clear_stage(); self.add(head)

        with self.say("metric"):
            self.cite("hartmann2023siebert")
            m = MathTex(r"\text{continuation}\ \longrightarrow\ \text{SiEBERT classifier}\ \longrightarrow\ P(\text{positive})\in[0,1]",
                        font_size=40)
            self.play(Write(m))
        self.play(FadeOut(m))

        with self.say("result"):
            self.cite("efron1993bootstrap", "holm1979", extra="our runs (data/study/*summary.json)")
            png = Image.open(ROOT / "data" / "study" / "exp02_dose_response_dark.png").convert("RGB")  # RGBA PNG -> RGB array
            fig = ImageMobject(np.array(png)).scale_to_fit_width(11.4).shift(UP * 0.55)
            self.play(FadeIn(fig))
            box = Rectangle(width=5.6, height=4.4, color=T.ALPHA).move_to(fig.get_center() + LEFT * 2.85)
            h1_2 = next(t for t in st2["secondary"] if t["contrast"] == "steer_5 - random_5")
            pr1, pr2 = st1["primary"], st2["primary"]
            res = VGroup(
                MathTex(r"\text{run 2: steered}(5)-\text{unsteered} = " + _ci(pr2["mean"], pr2["lo"], pr2["hi"]), font_size=30, color=T.ALPHA),
                MathTex(r"\text{steered}(5)-\text{random}(5):\ \text{run 1 } " + _ci(pr1["mean"], pr1["lo"], pr1["hi"])
                        + r",\ \text{run 2 } " + _ci(h1_2["mean"], h1_2["lo"], h1_2["hi"]), font_size=30, color=T.FG),
            ).arrange(DOWN, buff=0.15).next_to(fig, DOWN, buff=0.2)
            self.play(Create(box)); self.play(Write(res))
        self.play(FadeOut(box), FadeOut(res))

        with self.say("cost"):
            box2 = Rectangle(width=5.6, height=4.4, color=T.ALPHA).move_to(fig.get_center() + RIGHT * 2.85)
            self.play(Create(box2))
        self.wait(0.5)
