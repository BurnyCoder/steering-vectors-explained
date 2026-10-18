"""ch07_build.py — contrast pairs, ActAdd's h_A, CAA's dataset of triples, and the mean-difference formula.

Global context: builds equation (1), v_ℓ = (1/|D|) Σ [a_ℓ(p,c⁺) − a_ℓ(p,c⁻)] (CAA Eq. 1), part by part,
from operations defined in chapter 02. Toy numbers: toy.mean_difference; real numbers: GPT-2-XL
"Love" − "Hate" at layer 6 (practical_example.json). The A/B triple is an illustrative example in
CAA's multiple-choice format, labelled as such on screen.
"""

from manim import (DOWN, LEFT, RIGHT, UP, Brace, Create, FadeIn, FadeOut, GrowArrow, Indicate, MathTex, VGroup, Write)

from steering_explainer.video import theme as T
from steering_explainer.video import toy
from steering_explainer.video.formulas import v_equation
from steering_explainer.video.widgets import ChapterScene, arrow, example, num, plane, quote_card, text, token_row, tup


class Ch07(ChapterScene):
    CHAPTER = "ch07"

    def construct(self):
        ex = example()
        head = self.chapter_title()
        self.play(Write(head))

        with self.say("pair"):
            self.cite("turner2024actadd")
            plus = VGroup(MathTex("p^+", color=T.PLUS, font_size=44), token_row(ex["tokens_plus"], T.PLUS)).arrange(RIGHT, buff=0.4)
            minus = VGroup(MathTex("p^-", color=T.MINUS, font_size=44), token_row(ex["tokens_minus"], T.MINUS)).arrange(RIGHT, buff=0.4)
            pair = VGroup(plus, minus).arrange(DOWN, buff=0.4, aligned_edge=LEFT).shift(UP * 1.2)
            q = quote_card("actadd_single_pair", width=60).shift(DOWN * 1.4)
            self.play(FadeIn(pair, lag_ratio=0.3)); self.play(FadeIn(q))
        self.play(FadeOut(q))

        with self.say("actadd"):
            f = MathTex(r"h_A", r"=", r"h_\ell(p^+)", r"-", r"h_\ell(p^-)", r"\in\mathbb{R}^{n\times d}", font_size=50).shift(DOWN * 0.4)
            f[0].set_color(T.STEER); f[2].set_color(T.PLUS); f[4].set_color(T.MINUS); f[5].set_color(T.SET)
            n_note = text("one difference vector per position (n = number of tokens)", T.SIZE_SMALL, T.FG2).next_to(f, DOWN, buff=0.35)
            q = quote_card("actadd_padding", width=70, size=22).to_edge(DOWN, buff=0.6)
            self.play(Write(f)); self.play(FadeIn(n_note)); self.play(FadeIn(q))
        self.clear_stage(); self.add(head)

        with self.say("dataset"):
            self.cite("panickssery2024caa")
            D = MathTex(r"\mathcal{D}=\{(p,\,c^+,\,c^-),\ \dots\}", font_size=48, color=T.SET).shift(UP * 2.0)
            trip = VGroup(text("p:  Is the Great Wall of China visible from the Moon with the naked eye?  (A) Yes  (B) No", T.SIZE_SMALL, T.FG, 70),
                          text("c⁺:  (B)   ← factual", T.SIZE_SMALL, T.PLUS), text("c⁻:  (A)   ← hallucinated", T.SIZE_SMALL, T.MINUS)
                          ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).shift(UP * 0.5)
            ill = text("illustrative triple in CAA's A/B format", T.SIZE_SMALL - 6, T.MUTED).next_to(trip, DOWN, buff=0.12).align_to(trip, LEFT)
            a = MathTex(r"a_\ell(p,c)\in\mathbb{R}^d:\ \text{residual stream at layer }\ell\text{, last token of } c", font_size=36)
            a.next_to(ill, DOWN, buff=0.35).set_x(0)
            q = quote_card("caa_definition", width=80, size=20).to_edge(DOWN, buff=0.55)
            self.play(Write(D)); self.play(FadeIn(trip), FadeIn(ill)); self.play(Write(a)); self.play(FadeIn(q))
        self.clear_stage(); self.add(head)

        with self.say("formula"):
            eq = v_equation(56).shift(UP * 0.9)
            steps = [((4, 5, 6, 7, 8), "1. difference for one triple"), ((3,), "2. add over every triple in D"),
                     ((2,), "3. divide by |D|, the number of triples"), ((0,), "= the steering vector, an element of ℝ^d")]
            for k, (idx, label) in enumerate(steps):  # build right-to-left: bracket, Σ, 1/|D|, v_ℓ =
                part = VGroup(*[eq[i] for i in idx])
                self.play(Write(part) if k < 3 else Write(VGroup(eq[0], eq[1])))
                b = Brace(part, DOWN, color=T.FG2)
                t = text(label, T.SIZE_SMALL, T.FG2).next_to(b, DOWN, buff=0.1)
                self.play(FadeIn(b), FadeIn(t))
                self.wait(0.4)
                self.play(FadeOut(b), FadeOut(t))
            special = MathTex(r"\text{ActAdd} = \text{special case } |\mathcal{D}| = 1", font_size=40, color=T.FG2).shift(DOWN * 1.8)
            self.play(FadeIn(special))
        self.clear_stage(); self.add(head)

        with self.say("toy"):
            md = toy.mean_difference()
            pl = plane((-1, 3), (-1, 1), 1.4).shift(LEFT * 2.6 + DOWN * 0.2)
            diffs = [arrow(pl, d, T.FG2) for d in md["diffs"]]
            mean = arrow(pl, md["v"], T.STEER)
            rows = VGroup(*[MathTex(tup(d), font_size=36, color=T.FG2) for d in md["diffs"]],
                          MathTex(r"v=\tfrac13\textstyle\sum=" + tup(md["v"]), font_size=40, color=T.STEER)).arrange(DOWN, aligned_edge=LEFT).shift(RIGHT * 3.2)
            self.play(Create(pl))
            for d, r in zip(diffs, rows[:3]):
                self.play(GrowArrow(d), FadeIn(r), run_time=0.7)
            self.play(GrowArrow(mean), Write(rows[3]))
        self.clear_stage(); self.add(head)

        with self.say("real"):
            self.cite("turner2024actadd", extra="our measurement, GPT-2-XL layer 6")
            vals = ",\\ ".join(f"{x:.2f}" for x in ex["h_A_first6"])
            lines = VGroup(
                MathTex(rf"\|h_6(\text{{Love}})\| = {ex['h_plus_norm']:.1f},\qquad \|h_6(\text{{Hate}})\| = {ex['h_minus_norm']:.1f}", font_size=38),
                MathTex(rf"\cos = \hat h_6(\text{{Love}})\cdot \hat h_6(\text{{Hate}}) = {ex['cos_plus_minus']:.3f}", font_size=38),
                MathTex(rf"h_A^{{(1)}} = \big({vals},\ \dots\big),\qquad \|h_A^{{(1)}}\| = {ex['h_A_norm_per_pos'][1]:.1f}", font_size=36, color=T.STEER),
                MathTex(rf"h_A^{{(0)}} = 0 \quad(\text{{both start with }} \langle|\text{{endoftext}}|\rangle)", font_size=36, color=T.FG2),
            ).arrange(DOWN, buff=0.45)
            for ln in lines:
                self.play(Write(ln), run_time=1.2)
        self.wait(0.5)
