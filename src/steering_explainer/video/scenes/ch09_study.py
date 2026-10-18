"""ch09_study.py — our pre-registered dose-response test with a random-direction control.

Global context: shows the design (reports/exp01_preregistration.md), the control idea, the metric,
and the measured result figure (study/plots.py, dark theme) with numbers from
data/study/summary.json — narrated through narration_values.py, whatever the verdict is.
"""

import math

from manim import (DOWN, LEFT, RIGHT, UP, Circle, Create, DashedVMobject, FadeIn, FadeOut, GrowArrow, ImageMobject,
                   MathTex, Rectangle, VGroup, Write)

from steering_explainer.config import ROOT
from steering_explainer.video import theme as T
from steering_explainer.video.widgets import ChapterScene, arrow, plane, study, text


class Ch09(ChapterScene):
    CHAPTER = "ch09"

    def construct(self):
        st = study()
        head = self.chapter_title()
        self.play(Write(head))

        with self.say("question"):
            self.cite("maas2011imdb", extra="IMDb review openings, first 8 words")
            alphas = ",\\ ".join(f"{a:g}" for a in sorted({float(k.split('_')[1]) for k in st["means"]["p_pos"] if k.startswith("steer_")}))
            design = MathTex(rf"{st['n_prompts']}\ \text{{prompts}}\ \times\ \alpha\in\{{{alphas}\}}\ \times\ {len(st['seeds'])}\ \text{{samples}}",
                             font_size=44).shift(UP * 1.6)
            ex = VGroup(*[text(f"“{e['prompt']} …”", T.SIZE_SMALL, T.FG2) for e in st["examples"]]).arrange(DOWN, aligned_edge=LEFT).shift(DOWN * 0.1)
            pre = text("plan written and committed before any data: reports/exp01_preregistration.md", T.SIZE_SMALL, T.PLUS).shift(DOWN * 2.0)
            self.play(Write(design)); self.play(FadeIn(ex, lag_ratio=0.3)); self.play(FadeIn(pre))
        self.clear_stage(); self.add(head)

        with self.say("control"):
            pl = plane((-3, 3), (-3, 3), 0.75).shift(LEFT * 3 + DOWN * 0.3)
            v = arrow(pl, (2, 0), T.STEER)
            angles = [0.9, 2.0, 2.9, 4.1, 5.2]  # fixed illustrative angles for 5 random directions
            rnd = [arrow(pl, (2 * math.cos(a), 2 * math.sin(a)), "#d95926") for a in angles]
            ring = DashedVMobject(Circle(radius=2 * 0.75, color=T.MUTED).move_to(pl.c2p(0, 0)), num_dashes=40)
            cap = VGroup(text("steering vector v", T.SIZE_SMALL, T.STEER), text("random directions, same norm ‖v‖", T.SIZE_SMALL, "#d95926"),
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
            self.cite("efron1993bootstrap", extra="our study (data/study/summary.json)")
            fig = ImageMobject(str(ROOT / "data" / "study" / "dose_response_dark.png")).scale_to_fit_width(13).shift(DOWN * 0.1)
            self.play(FadeIn(fig))
            pr = st["primary"]
            box = Rectangle(width=6.3, height=5.2, color=T.ALPHA).move_to(fig.get_center() + LEFT * 3.25)
            res = MathTex(rf"\Delta_{{\alpha=5}}(\text{{steer}}-\text{{random}}) = {pr['mean']:+.3f}\ \ [{pr['lo']:+.3f},\ {pr['hi']:+.3f}]",
                          font_size=34, color=T.ALPHA).to_edge(DOWN, buff=0.55)
            self.play(Create(box)); self.play(Write(res))
        self.play(FadeOut(box), FadeOut(res))

        with self.say("cost"):
            box2 = Rectangle(width=6.3, height=5.2, color=T.ALPHA).move_to(fig.get_center() + RIGHT * 3.25)
            self.play(Create(box2))
        self.wait(0.5)
