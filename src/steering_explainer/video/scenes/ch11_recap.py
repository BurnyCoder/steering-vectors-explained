"""ch11_recap.py — the two equations again, every symbol annotated with its set and a one-sentence meaning.

Global context: closes the loop opened in chapter 00 (same formulas.py objects). Each row uses only
notation defined in chapters 01-08 (ℝ, ℝ^d, ∈, sets written with braces).
"""

from manim import DOWN, LEFT, RIGHT, UP, FadeIn, FadeOut, VGroup, Write

from steering_explainer.video import theme as T
from steering_explainer.video.formulas import h_equation, v_equation
from steering_explainer.video.widgets import ChapterScene, symbol_row, text

ROWS = [  # symbol, belongs to, one-sentence meaning
    (r"v_\ell", r"\in\mathbb{R}^d", "steering vector for layer ℓ (ActAdd: one per position t)", T.STEER),
    (r"\ell", r"\in\{0,\dots,L-1\}", "which layer's input is edited", T.FG),
    (r"\mathcal{D}", r"=\{(p,c^+,c^-),\dots\}", "finite set of contrast triples", T.SET),
    (r"|\mathcal{D}|", r"\in\{1,2,3,\dots\}", "number of triples", T.SET),
    (r"p,\ c^+,\ c^-", r"\text{token sequences}", "prompt; behaviour shown / its opposite", T.PLUS),
    (r"a_\ell(p,c)", r"\in\mathbb{R}^d", "residual stream at layer ℓ, at the answer letter of c", T.FG),
    (r"h_\ell^{(t)}", r"\in\mathbb{R}^d", "residual stream entering layer ℓ at position t", T.VEC),
    (r"\alpha", r"\in\mathbb{R}", "steering coefficient: strength and sign", T.ALPHA),
    (r"T", r"\text{set of positions } t", "where the vector is added", T.SET),
    (r"\tilde h_\ell^{(t)}", r"\in\mathbb{R}^d", "steered activation, fed into layer ℓ", T.VEC),
]


def _column(rows: list[VGroup]) -> VGroup:
    """Align a list of (symbol, set, meaning) rows into three left-aligned sub-columns."""
    w_sym = max(r[0].width for r in rows)
    w_set = max(r[1].width for r in rows)
    for i, r in enumerate(rows):
        y = -i * 0.5
        r[0].move_to([0, y, 0], aligned_edge=LEFT)
        r[1].move_to([w_sym + 0.3, y, 0], aligned_edge=LEFT)
        r[2].move_to([w_sym + w_set + 0.6, y, 0], aligned_edge=LEFT)
    return VGroup(*rows)


class Ch11(ChapterScene):
    CHAPTER = "ch11"

    def construct(self):
        head = self.chapter_title()
        self.play(Write(head))

        with self.say("recap"):
            eqs = VGroup(v_equation(42), h_equation(42)).arrange(DOWN, buff=0.3).next_to(head, DOWN, buff=0.3)
            self.play(Write(eqs), run_time=2)
            rows = [symbol_row(s, m, d, c) for s, m, d, c in ROWS]
            table = _column(rows)  # one column: symbol | set | meaning
            table.scale_to_fit_height(min(table.height, 4.2))
            if table.width > 13:
                table.scale_to_fit_width(13)
            table.next_to(eqs, DOWN, buff=0.35).set_x(0)
            for r in rows:
                self.play(FadeIn(r), run_time=0.45)

        with self.say("outro"):
            end = VGroup(text("Build a direction from contrasting examples, then add it while the model runs.", T.SIZE_BODY, T.FG),
                         text("github.com/BurnyCoder/steering-vectors-explained", T.SIZE_SMALL, T.VEC),
                         text("code · data · every source and quote: see the description", T.SIZE_SMALL, T.FG2)
                         ).arrange(DOWN, buff=0.25)
            end.scale_to_fit_width(min(end.width, 12.8)).to_edge(DOWN, buff=0.4)
            self.play(FadeOut(table), FadeIn(end, lag_ratio=0.3))
        self.wait(1.5)
