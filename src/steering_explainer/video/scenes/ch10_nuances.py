"""ch10_nuances.py — limits of steering (coefficient, layer, access, reliability) and close relatives.

Global context: every claim here is a verified quote (data/sources.yaml). Visuals are synced to the
narration with manim-voiceover bookmarks (<bookmark mark='x'/> in data/script.yaml), whose times come
from edge-tts word boundaries (video/tts_edge.py). Directional ablation is written with the dot
product from chapter 02: x' = x − (r̂·x) r̂ (Arditi et al. 2024 Eq. 4 writes x − r̂ r̂ᵀ x, the same vector).
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
            self.cite("turner2024actadd", "tan2024generalization")
            # 3 × 2 grid in narration order; the layer-choice card explains why our example uses layer 6 of 48
            ids = ("actadd_coeff_limit", "actadd_middle_layers", "actadd_layer_choice", "actadd_api_access", "tan_variable",
                   "tan_anti_steerable")
            cards = [quote_card(q, 44, 22) for q in ids]
            grid = VGroup(*[VGroup(cards[i], cards[i + 1]).arrange(RIGHT, buff=0.6, aligned_edge=UP) for i in (0, 2, 4)]
                          ).arrange(DOWN, buff=0.4)
            grid.scale_to_fit_width(13)
            if grid.height > 5.6:
                grid.scale_to_fit_height(5.6)  # stay clear of the title and the footer
            grid.next_to(head, DOWN, buff=0.4)
            for mark, card in zip(("coeff", "middle", "layer", "api", "tan", "anti"), cards):
                self.wait_until_bookmark(mark)
                self.play(FadeIn(card), run_time=0.6)
        self.clear_stage(); self.add(head)

        with self.say("relatives"):
            self.wait_until_bookmark("iti")
            self.cite("li2023iti", "zou2023repe")
            q1 = quote_card("iti_definition", 70, 26).shift(UP * 1.2)
            self.play(FadeIn(q1), run_time=0.6)
            self.wait_until_bookmark("repe")
            q2 = quote_card("repe_reading_control", 70, 26).next_to(q1, DOWN, buff=0.5)  # supports "reads and controls"
            self.play(FadeIn(q2), run_time=0.6)

            self.wait_until_bookmark("abl")
            self.play(FadeOut(VGroup(q1, q2)), run_time=0.4)
            self.cite("arditi2024refusal")
            pl = plane((-1, 4), (-1, 3), 1.0).shift(LEFT * 3.3 + DOWN * 0.4)
            r, x = arrow(pl, (1, 0), T.STEER), arrow(pl, (3, 2), T.VEC)  # r̂ (unit) and x
            proj, x_ab = arrow(pl, (3, 0), T.ALPHA), arrow(pl, (0, 2), T.PLUS)  # (r̂·x) r̂ and x − (r̂·x) r̂
            drop = DashedLine(pl.c2p(3, 2), pl.c2p(3, 0), color=T.MUTED)
            f = MathTex(r"x' = x - (\hat r\cdot x)\,\hat r", font_size=52).shift(RIGHT * 3 + UP * 1.7)
            lab = VGroup(text("r̂: unit vector of the direction", T.SIZE_SMALL, T.STEER),
                         text("(r̂·x) r̂: projection, the part of x along r̂", T.SIZE_SMALL, T.ALPHA),
                         text("x′: x with that direction removed", T.SIZE_SMALL, T.PLUS)).arrange(DOWN, aligned_edge=LEFT).next_to(f, DOWN, buff=0.4)
            self.play(Create(pl), GrowArrow(x), GrowArrow(r), Write(f), FadeIn(lab[0]))
            self.wait_until_bookmark("proj")
            self.play(Create(drop), GrowArrow(proj), FadeIn(lab[1]))
            self.play(GrowArrow(x_ab), FadeIn(lab[2]))
            self.wait_until_bookmark("arditi")
            q3 = quote_card("arditi_one_dim", 40, 24).to_edge(DOWN, buff=0.6).shift(RIGHT * 3)
            self.play(FadeIn(q3), run_time=0.6)

            self.wait_until_bookmark("gg")
            self.clear_stage(run_time=0.4)
            self.add(head)
            self.cite("templeton2024scaling", "anthropic2024goldengate")
            gg = VGroup(quote_card("templeton_clamp", 60, 26), quote_card("goldengate_surgical", 60, 26)).arrange(DOWN, buff=0.5)
            self.play(FadeIn(gg, lag_ratio=0.4))
        self.wait(0.5)
