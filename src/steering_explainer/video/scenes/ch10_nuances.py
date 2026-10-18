"""ch10_nuances.py — limits of steering (coefficient, layer, access, reliability) and close relatives.

Global context: every claim here is a verified quote (data/sources.yaml). Directional ablation is
written with the dot product from chapter 02: x' = x − (r̂·x) r̂ (Arditi et al. 2024 Eq. 4 writes
x − r̂ r̂ᵀ x, which is the same vector).
"""

from manim import DOWN, LEFT, RIGHT, UP, Create, DashedLine, FadeIn, FadeOut, GrowArrow, MathTex, VGroup, Write

from steering_explainer.video import theme as T
from steering_explainer.video.widgets import ChapterScene, arrow, plane, quote_card, text


class Ch10(ChapterScene):
    CHAPTER = "ch10"

    def construct(self):
        head = self.chapter_title()
        self.play(Write(head))

        with self.say("limits"):
            self.cite("turner2024actadd", "tan2024generalization", "panickssery2024caa")
            cards = VGroup(quote_card("actadd_coeff_limit", 44, 22), quote_card("actadd_middle_layers", 44, 22),
                           quote_card("actadd_api_access", 44, 22), quote_card("tan_variable", 44, 22))
            top = VGroup(cards[0], cards[1]).arrange(RIGHT, buff=0.6, aligned_edge=UP)
            bottom = VGroup(cards[2], cards[3]).arrange(RIGHT, buff=0.6, aligned_edge=UP)
            grid = VGroup(top, bottom).arrange(DOWN, buff=0.6).scale_to_fit_width(13).shift(DOWN * 0.1)
            for c in (cards[0], cards[1], cards[2], cards[3]):
                self.play(FadeIn(c), run_time=0.8)
                self.wait(1.2)
            anti = quote_card("tan_anti_steerable", 80, 20).to_edge(DOWN, buff=0.55)
            self.play(grid.animate.shift(UP * 0.4), FadeIn(anti))
        self.clear_stage(); self.add(head)

        with self.say("relatives"):
            self.cite("li2023iti", "zou2023repe")
            q1 = quote_card("iti_definition", 70, 22).shift(UP * 1.6)
            q2 = quote_card("repe_definition", 70, 22).next_to(q1, DOWN, buff=0.4)
            self.play(FadeIn(q1)); self.play(FadeIn(q2))
            self.play(FadeOut(VGroup(q1, q2)))
            self.cite("arditi2024refusal")
            pl = plane((-1, 4), (-1, 3), 0.95).shift(LEFT * 3.3 + DOWN * 0.5)
            r = arrow(pl, (1, 0), T.STEER)  # r̂ (unit vector)
            x = arrow(pl, (3, 2), T.VEC)
            proj = arrow(pl, (3, 0), T.ALPHA)  # (r̂·x) r̂
            x_ab = arrow(pl, (0, 2), T.PLUS)  # x − (r̂·x) r̂
            drop = DashedLine(pl.c2p(3, 2), pl.c2p(3, 0), color=T.MUTED)
            f = MathTex(r"x' = x - (\hat r\cdot x)\,\hat r", font_size=48).shift(RIGHT * 3 + UP * 1.6)
            lab = VGroup(text("r̂: unit vector of the direction", T.SIZE_SMALL, T.STEER),
                         text("(r̂·x) r̂: projection = part of x along r̂", T.SIZE_SMALL, T.ALPHA),
                         text("x′: x with that direction removed", T.SIZE_SMALL, T.PLUS)).arrange(DOWN, aligned_edge=LEFT).next_to(f, DOWN, buff=0.4)
            q3 = quote_card("arditi_one_dim", 40, 22).to_edge(DOWN, buff=0.6).shift(RIGHT * 3)
            self.play(Create(pl), GrowArrow(x), GrowArrow(r), Write(f))
            self.play(Create(drop), GrowArrow(proj), FadeIn(lab[:2]))
            self.play(GrowArrow(x_ab), FadeIn(lab[2]), FadeIn(q3))
            self.clear_stage()
            self.add(head)
            self.cite("templeton2024scaling", "anthropic2024goldengate")
            gg = VGroup(quote_card("templeton_clamp", 60, 24), quote_card("goldengate_surgical", 60, 24)).arrange(DOWN, buff=0.5)
            self.play(FadeIn(gg, lag_ratio=0.4))
        self.wait(0.5)
