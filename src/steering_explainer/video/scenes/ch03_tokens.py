"""ch03_tokens.py — functions, tokenizer, tokens, vocabulary V and |V|, positions t, embeddings.

Global context: the real token split and IDs of "I hate you because" come from GPT-2's tokenizer
(practical_example.json); |V| = 50,257 is both read from the model config and quoted from the GPT-2
report (Radford et al. 2019, verified in data/sources.yaml).
"""

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Dot, Ellipse, FadeIn, FadeOut, GrowArrow, MathTex, VGroup, Write)

from steering_explainer.video import theme as T
from steering_explainer.video import toy
from steering_explainer.video.widgets import ChapterScene, example, quote_card, text, token_row, tup


class Ch03(ChapterScene):
    CHAPTER = "ch03"

    def construct(self):
        ex = example()
        head = self.chapter_title()
        self.play(Write(head))

        with self.say("function"):
            X = Ellipse(width=2.2, height=3, color=T.SET).shift(LEFT * 2.5)
            Y = Ellipse(width=2.2, height=3, color=T.SET).shift(RIGHT * 2.5)
            xs = [Dot(X.get_center() + UP * y, color=T.FG) for y in (0.8, 0, -0.8)]
            ys = [Dot(Y.get_center() + UP * y, color=T.FG) for y in (0.6, -0.6)]
            maps = [Arrow(xs[0].get_center(), ys[0].get_center(), buff=0.1, color=T.FG2),
                    Arrow(xs[1].get_center(), ys[0].get_center(), buff=0.1, color=T.FG2),
                    Arrow(xs[2].get_center(), ys[1].get_center(), buff=0.1, color=T.FG2)]
            lab = MathTex(r"f: X \to Y", font_size=52).shift(UP * 2.2)
            names = VGroup(MathTex("X", color=T.SET).next_to(X, DOWN), MathTex("Y", color=T.SET).next_to(Y, DOWN))
            self.play(FadeIn(VGroup(X, Y, names, *xs, *ys)), Write(lab))
            self.play(*[GrowArrow(m) for m in maps])
        self.play(*[FadeOut(m) for m in (X, Y, names, lab, *xs, *ys, *maps)])

        with self.say("tokens"):
            self.cite("radford2019gpt2")
            flow = text("text  →  tokenizer  →  tokens (word pieces) with whole-number IDs", T.SIZE_SMALL, T.FG).shift(UP * 2)
            v = MathTex(r"V=\{\text{all tokens}\},\qquad |V| = " + f"{ex['model']['d_vocab']:,}".replace(",", "{,}"),
                        font_size=48, color=T.SET).shift(UP * 0.8)
            q = quote_card("gpt2_vocab").shift(DOWN * 1.0)
            self.play(FadeIn(flow))
            self.play(Write(v))
            self.play(FadeIn(q))
        self.play(FadeOut(VGroup(flow, v, q)))

        with self.say("example"):
            row = token_row(ex["tokens_prompt"], T.FG, 34, buff=0.45).shift(UP * 0.4)
            ids = VGroup(*[text(str(i), T.SIZE_SMALL, T.FG2).next_to(c, DOWN, buff=0.2) for i, c in zip(ex["token_ids_prompt"], row)])
            pos = VGroup(*[MathTex(f"t={k}", font_size=34, color=T.ALPHA).next_to(c, UP, buff=0.25) for k, c in enumerate(row)])
            cap = text("token IDs", T.SIZE_SMALL, T.FG2).next_to(ids, DOWN, buff=0.3)
            self.play(FadeIn(row, lag_ratio=0.2))
            self.play(FadeIn(ids), FadeIn(cap))
            self.play(FadeIn(pos, lag_ratio=0.2))
        self.play(FadeOut(VGroup(row, ids, pos, cap)))

        with self.say("embedding"):
            sig = MathTex(r"\mathrm{Embed}: V \to \mathbb{R}^d,\qquad h_0^{(t)} = e(\text{token}_t) + e(\text{position } t)",
                          font_size=42).shift(UP * 1.9)
            chips = token_row(list(toy.TOY_EMBED), T.FG, 32).arrange(DOWN, buff=0.35).shift(LEFT * 2 + DOWN * 0.6)
            vecs = VGroup(*[MathTex(tup(v), color=T.VEC, font_size=44).move_to([1.6, c.get_center()[1], 0], aligned_edge=LEFT)
                            for c, v in zip(chips, toy.TOY_EMBED.values())])
            arrows = VGroup(*[Arrow(c.get_right(), v.get_left(), buff=0.2, color=T.FG2) for c, v in zip(chips, vecs)])
            note = text("toy vocabulary, d = 2", T.SIZE_SMALL, T.FG2).next_to(chips, DOWN, buff=0.4)
            self.play(Write(sig))
            self.play(FadeIn(chips), FadeIn(note))
            self.play(*[GrowArrow(a) for a in arrows], FadeIn(vecs))
        self.wait(0.5)
