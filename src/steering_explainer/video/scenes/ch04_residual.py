"""ch04_residual.py — layers ℓ, L, attention, MLP, the residual stream, activations h_ℓ^(t), forward pass.

Global context: steering edits exactly this object — the residual stream entering layer ℓ. The
update rule is GPT-2's pre-LayerNorm block (Radford et al. 2019 §2.3): Attn_ℓ and MLP_ℓ normalise their own
input, so the residual sum itself is exact (notation as in Arditi et al. 2024, Eq. 1); the Elhage et al. (2021) quote is verified verbatim in data/sources.yaml. The real norm of
h_6 at the token " hate" comes from practical_example.json.
"""

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Circle, Create, FadeIn, FadeOut, GrowArrow, Line, MathTex,
                   RoundedRectangle, SurroundingRectangle, VGroup, Write)

from steering_explainer.video import theme as T
from steering_explainer.video import toy
from steering_explainer.video.widgets import ChapterScene, arrow, example, plane, quote_card, text, tup


def _box(label: str, color: str, w: float = 1.6, h: float = 0.8) -> VGroup:
    tex = MathTex(label, font_size=34, color=color)
    return VGroup(RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color), tex)


class Ch04(ChapterScene):
    CHAPTER = "ch04"

    def construct(self):
        ex = example()
        L = ex["model"]["n_layers"]
        head = self.chapter_title()
        self.play(Write(head))

        with self.say("layers"):
            self.cite("radford2019gpt2", "vaswani2017")
            names = ["0", "1", r"\cdots", str(L - 1)]
            stack = VGroup(*[_box(rf"\text{{layer }}{n}" if n != r"\cdots" else n, T.FG2, 2.6, 0.7) for n in names])
            stack.arrange(RIGHT, buff=0.35).shift(UP * 0.6)
            lab = MathTex(rf"L = {L},\qquad \ell \in \{{0, 1, \dots, L-1\}}", font_size=44).next_to(stack, DOWN, buff=0.6)
            self.play(FadeIn(stack, lag_ratio=0.2))
            self.play(Write(lab))
        self.play(FadeOut(VGroup(stack, lab)))

        with self.say("parts"):
            attn = _box(r"\mathrm{Attn}_\ell", T.PLUS, 2.0).shift(LEFT * 2.5 + UP * 0.8)
            mlp = _box(r"\mathrm{MLP}_\ell", T.STEER, 2.0).shift(RIGHT * 2.5 + UP * 0.8)
            da = text("attention: each position gathers information from itself and earlier positions", T.SIZE_SMALL, T.FG2, 30).next_to(attn, DOWN)
            dm = text("MLP (multilayer perceptron): transforms each position's vector on its own", T.SIZE_SMALL, T.FG2, 30).next_to(mlp, DOWN)
            causal = quote_card("vaswani_causal", width=70, size=22).to_edge(DOWN, buff=0.95)  # "itself and earlier"
            self.play(FadeIn(attn), FadeIn(da), FadeIn(causal))
            self.play(FadeIn(mlp), FadeIn(dm))
        self.play(FadeOut(VGroup(da, dm, causal)))

        with self.say("residual"):
            self.cite("elhage2021framework", "radford2019gpt2", "arditi2024refusal")
            stream = Line(LEFT * 6, RIGHT * 6, color=T.VEC, stroke_width=6).shift(DOWN * 0.25)
            p1, p2 = Circle(0.22, color=T.FG).move_to(stream.point_from_proportion(0.38)), Circle(0.22, color=T.FG).move_to(stream.point_from_proportion(0.7))
            plus = VGroup(*[MathTex("+", font_size=36).move_to(c) for c in (p1, p2)])
            self.play(attn.animate.move_to(p1.get_center() + UP * 1.4), mlp.animate.move_to(p2.get_center() + UP * 1.4))
            reads = VGroup(Arrow(stream.point_from_proportion(0.3), attn.get_bottom() + LEFT * 0.3, buff=0.05, color=T.FG2),
                           Arrow(attn.get_bottom() + RIGHT * 0.3, p1.get_top(), buff=0.05, color=T.PLUS),
                           Arrow(stream.point_from_proportion(0.62), mlp.get_bottom() + LEFT * 0.3, buff=0.05, color=T.FG2),
                           Arrow(mlp.get_bottom() + RIGHT * 0.3, p2.get_top(), buff=0.05, color=T.STEER))
            hl = MathTex(r"h_\ell", color=T.VEC, font_size=38).next_to(stream, LEFT, buff=0.1).shift(RIGHT * 0.6 + DOWN * 0.4)
            hr = MathTex(r"h_{\ell+1}", color=T.VEC, font_size=38).next_to(stream, RIGHT, buff=0.1).shift(LEFT * 0.8 + DOWN * 0.4)
            eq = MathTex(r"h_{\ell+1}=h_\ell+\mathrm{Attn}_\ell(h_\ell)+\mathrm{MLP}_\ell\big(h_\ell+\mathrm{Attn}_\ell(h_\ell)\big)",
                         font_size=38).shift(DOWN * 1.3)
            self.play(Create(stream), FadeIn(hl), FadeIn(hr))
            self.play(FadeIn(VGroup(p1, p2, plus)), *[GrowArrow(a) for a in reads])
            ln = text("each part normalizes what it reads (pre-LayerNorm); what it writes is added unchanged",
                      T.SIZE_SMALL, T.FG2).next_to(head, DOWN, buff=0.35)
            self.play(Write(eq), FadeIn(ln))
            q = quote_card("elhage_residual_sum", width=95, size=20).next_to(eq, DOWN, buff=0.25)  # clear of the footer
            self.play(FadeIn(q))
        self.clear_stage()
        self.add(head)

        with self.say("toy"):
            r = toy.residual_toy()
            pl = plane((-1, 3), (-1, 2), 1.2).shift(LEFT * 2.5 + DOWN * 0.4)
            a0 = arrow(pl, r["h0"], T.VEC)
            a1 = arrow(pl, r["attn"], T.PLUS, start=r["h0"])
            a2 = arrow(pl, r["mlp"], T.STEER, start=r["after_attn"])
            res = arrow(pl, r["h1"], T.ALPHA)
            steps = VGroup(MathTex(r"h_0=" + tup(r["h0"]), color=T.VEC, font_size=40),
                           MathTex(r"+\ \mathrm{Attn}:\ " + tup(r["attn"]) + r"\ \Rightarrow\ " + tup(r["after_attn"]), font_size=40),
                           MathTex(r"+\ \mathrm{MLP}:\ " + tup(r["mlp"]) + r"\ \Rightarrow\ h_1=" + tup(r["h1"]), font_size=40)
                           ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).shift(RIGHT * 3 + UP * 0.2)
            self.play(Create(pl), GrowArrow(a0), Write(steps[0]))
            self.play(GrowArrow(a1), Write(steps[1]))
            self.play(GrowArrow(a2), Write(steps[2]))
            self.play(GrowArrow(res))
        self.clear_stage()
        self.add(head)

        with self.say("activation"):
            self.cite("radford2019gpt2", extra="our measurement (data/practical_example.json)")
            notation = MathTex(r"h_\ell^{(t)} \in \mathbb{R}^d", font_size=64).shift(UP * 1.6)
            notation[0][0].set_color(T.VEC)
            legend = VGroup(text("ℓ = which layer it enters", T.SIZE_SMALL, T.FG2), text("t = which position (token)", T.SIZE_SMALL, T.FG2)
                            ).arrange(DOWN, aligned_edge=LEFT).next_to(notation, DOWN, buff=0.3)
            hate_pos = ex["tokens_prompt"].index(" hate")
            lay = ex["layer"]  # the steered layer (practical_example.json), not a typed number
            real = MathTex(rf"\text{{GPT-2-XL: }}\ h_{{{lay}}}^{{({hate_pos})}}\ (\text{{token ``hate''}})\in\mathbb{{R}}^{{{ex['model']['d_model']}}},\quad "
                           rf"\|h_{{{lay}}}^{{({hate_pos})}}\| = {ex['h_prompt_norm_per_pos'][hate_pos]:.1f}", font_size=36).shift(DOWN * 1.4)
            fp = text("forward pass = one run through all L layers", T.SIZE_SMALL, T.FG).shift(DOWN * 2.4)
            self.play(Write(notation)); self.play(FadeIn(legend))
            self.play(Write(real)); self.play(FadeIn(fp))
        self.wait(0.5)
