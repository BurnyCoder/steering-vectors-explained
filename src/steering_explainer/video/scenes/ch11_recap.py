"""ch11_recap.py — the two equations again, every symbol annotated with its set and a one-sentence meaning.

Global context: closes the loop opened in chapter 00 (same formulas.py objects). Each row uses only
notation defined in chapters 01-08 (ℝ, ℝ^d, ∈, sets written with braces).
"""

from manim import DOWN, LEFT, RIGHT, UP, FadeIn, VGroup, Write

from steering_explainer.video import theme as T
from steering_explainer.video.formulas import h_equation, v_equation
from steering_explainer.video.widgets import ChapterScene, symbol_row, text

ROWS = [  # symbol, belongs to, one-sentence meaning
    (r"v_\ell", r"\in\mathbb{R}^d", "steering vector for layer ℓ", T.STEER),
    (r"\ell", r"\in\{0,\dots,L-1\}", "which layer's input is edited", T.FG),
    (r"\mathcal{D}", r"=\{(p,c^+,c^-),\dots\}", "finite set of contrast triples", T.SET),
    (r"|\mathcal{D}|", r"\in\{1,2,3,\dots\}", "number of triples", T.SET),
    (r"p,\ c^+,\ c^-", r"\text{token sequences}", "prompt, behaviour shown / opposite", T.PLUS),
    (r"a_\ell(p,c)", r"\in\mathbb{R}^d", "residual stream at layer ℓ, last token of c", T.FG),
    (r"h_\ell^{(t)}", r"\in\mathbb{R}^d", "residual stream entering layer ℓ at position t", T.VEC),
    (r"\alpha", r"\in\mathbb{R}", "steering coefficient: strength and sign", T.ALPHA),
    (r"T", r"\text{set of positions } t", "where the vector is added", T.SET),
    (r"\tilde h_\ell^{(t)}", r"\in\mathbb{R}^d", "steered activation passed on to later layers", T.VEC),
]


class Ch11(ChapterScene):
    CHAPTER = "ch11"

    def construct(self):
        head = self.chapter_title()
        self.play(Write(head))

        with self.say("recap"):
            eqs = VGroup(v_equation(40), h_equation(40)).arrange(DOWN, buff=0.3).next_to(head, DOWN, buff=0.35)
            self.play(Write(eqs), run_time=2)
            rows = [symbol_row(s, m, d, c) for s, m, d, c in ROWS]
            for r in rows:
                r[0].scale(0.85); r[1].scale(0.85); r[2].scale(0.8)
            col_w = [max(r[i].width for r in rows) for i in range(3)]
            table = VGroup()
            for i, r in enumerate(rows):  # two columns of five rows
                col, k = divmod(i, 5)
                x0 = -6.6 + col * 6.9
                y = 0.4 - k * 0.62
                r[0].move_to([x0, y, 0], aligned_edge=LEFT)
                r[1].move_to([x0 + col_w[0] * 0.85 + 0.2, y, 0], aligned_edge=LEFT)
                r[2].next_to(r[1], RIGHT, buff=0.2)
                table.add(r)
            table.scale_to_fit_width(13.4).next_to(eqs, DOWN, buff=0.45)
            for r in table:
                self.play(FadeIn(r), run_time=0.45)

        with self.say("outro"):
            end = VGroup(text("Build a direction from contrasting examples → add it while the model runs.", T.SIZE_BODY, T.FG),
                         text("github.com/BurnyCoder/steering-vectors-explained", T.SIZE_SMALL, T.VEC),
                         text("code · data · every source and quote: see the description", T.SIZE_SMALL, T.FG2)
                         ).arrange(DOWN, buff=0.3).to_edge(DOWN, buff=0.35)
            self.play(table.animate.set_opacity(0.35), FadeIn(end, lag_ratio=0.3))
        self.wait(1.5)
