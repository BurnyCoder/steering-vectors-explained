"""ch05_softmax.py — matrices, the unembedding W_U, logits, softmax, sampling; real next-token probabilities.

Global context: steering changes the final residual stream, hence the logits W_U LN(h_L), hence these
probabilities — this chapter is the readout that chapter 08 shows moving. The toy matrix is the
3-token unembedding reused in chapter 08 (video/toy.py); the softmax(2,1,0) numbers are pinned by
tests/test_toy.py; the real top-5 comes from practical_example.json.
"""

from manim import DOWN, LEFT, RIGHT, UP, FadeIn, FadeOut, MathTex, Matrix, VGroup, Write, CurvedArrow

from steering_explainer.video import theme as T
from steering_explainer.video import toy
from steering_explainer.video.widgets import ChapterScene, example, num, prob_bars, quote_card, text


class Ch05(ChapterScene):
    CHAPTER = "ch05"

    def construct(self):
        ex = example()
        st = toy.steering_toy()
        head = self.chapter_title()
        self.play(Write(head))

        with self.say("matrix"):
            W = Matrix([[num(x) for x in row] for row in st["w_u"]], h_buff=1.0).set_color(T.FG)
            h = Matrix([[num(x)] for x in st["h"]]).set_color(T.VEC)
            out = Matrix([[num(x)] for x in st["logits_before"]]).set_color(T.ALPHA)
            eq = VGroup(W, MathTex(r"\cdot"), h, MathTex("="), out).arrange(RIGHT, buff=0.3).shift(UP * 0.5)
            names = VGroup(*[text(f"“{tk.strip()}”", T.SIZE_SMALL, T.FG2).next_to(row, LEFT, buff=0.5).set_y(row.get_y())
                             for tk, row in zip(st["tokens"], W.get_rows())])  # which token each row scores
            r0, hv = st["w_u"][0], st["h"]
            rows = text(f"each output = (row of the matrix) · (vector): e.g. ({num(r0[0])}, {num(r0[1])})·({num(hv[0])}, {num(hv[1])})"
                        f" = {num(st['logits_before'][0])}", T.SIZE_SMALL, T.FG2).shift(DOWN * 1.6)
            self.play(FadeIn(eq, lag_ratio=0.2))
            self.play(FadeIn(names), FadeIn(rows))
        self.play(FadeOut(VGroup(eq, names, rows)))

        with self.say("logits"):
            self.cite("radford2019gpt2", "hf_gpt2_model")  # GPT-2 normalises the final stream (ln_f) before the LM head
            wu = MathTex(r"W_U \in \mathbb{R}^{|V|\times d}", r"\qquad z = W_U\, \mathrm{LN}(h_L) \in \mathbb{R}^{|V|}", font_size=48).shift(UP * 0.8)
            cap = text("one row per token → one score (logit) per token;  LN = one last normalization",
                       T.SIZE_SMALL, T.FG2).next_to(wu, DOWN, buff=0.5)
            q = quote_card("gpt2_final_ln", width=70, size=22).to_edge(DOWN, buff=0.6)
            self.play(Write(wu)); self.play(FadeIn(cap), FadeIn(q))
        self.play(FadeOut(VGroup(wu, cap, q)))
        self.uncite()

        with self.say("softmax"):
            f = MathTex(r"\mathrm{softmax}(z)_i=\frac{e^{z_i}}{\sum_j e^{z_j}}", font_size=52).shift(UP * 1.7)
            z = [2, 1, 0]
            p = toy.softmax(z)
            ex1 = MathTex(r"z=(2,1,0)\ \Rightarrow\ p=(" + ",".join(f"{x:.3f}" for x in p) + r"),\quad \textstyle\sum_i p_i = 1",
                          font_size=40).next_to(f, DOWN, buff=0.5)
            bars = prob_bars(["token 1", "token 2", "token 3"], p, T.VEC, 5, tokens=False).next_to(ex1, DOWN, buff=0.6)
            self.play(Write(f)); self.play(Write(ex1)); self.play(FadeIn(bars, lag_ratio=0.2))
        self.play(FadeOut(VGroup(f, ex1, bars)))

        with self.say("sampling"):
            self.cite("actadd_code", extra="our measurement (data/practical_example.json)")
            top = ex["next_token"]["unsteered_top5"]
            title = text(f"GPT-2-XL, after “{ex['prompt']}”: next-token probabilities (top 5)", T.SIZE_SMALL, T.FG)
            bars = prob_bars([t for t, _ in top], [q for _, q in top], T.VEC, max_width=6)
            loop = text("sample a token → append it → repeat", T.SIZE_SMALL, T.ALPHA)
            smp = ex["sampling"]  # ActAdd's sampler settings (quote card), used for every completion in this video
            how = text(f"our runs, as in ActAdd: temperature {smp['temperature']:g}, top-p {smp['top_p']:g} (sample only among the "
                       f"most likely tokens), frequency penalty {smp['freq_penalty']:g} (discourage repeats)", T.SIZE_SMALL - 4, T.FG2, 80)
            q = quote_card("code_sampling_kwargs", width=60, size=20)
            col = VGroup(title, bars, loop, how, q).arrange(DOWN, buff=0.3)
            if col.height > 5.7:
                col.scale_to_fit_height(5.7)  # title bar above, footer below
            col.next_to(head, DOWN, buff=0.35)
            self.play(FadeIn(title)); self.play(FadeIn(bars, lag_ratio=0.2)); self.play(FadeIn(loop))
            self.play(FadeIn(how), FadeIn(q))
        self.wait(0.5)
