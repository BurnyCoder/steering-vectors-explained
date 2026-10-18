"""ch01_vectors.py — scalars, ℝ, ∈, vectors, components, dimension d, ℝ^d; GPT-2-XL's d = 1600.

Global context: the first building blocks; every later chapter writes activations as vectors in ℝ^d.
Practical numbers (d, parameter count) come from the loaded model config via practical_example.json.
"""

from manim import DOWN, LEFT, RIGHT, UP, Arrow, Brace, Create, FadeIn, FadeOut, GrowArrow, MathTex, VGroup, Write

from steering_explainer.video import theme as T
from steering_explainer.video.widgets import ChapterScene, arrow, definition_card, example, plane, text


class Ch01(ChapterScene):
    CHAPTER = "ch01"

    def construct(self):
        ex = example()
        head = self.chapter_title()
        self.play(Write(head))

        with self.say("scalar"):
            nums = VGroup(*[MathTex(s, color=T.ALPHA, font_size=64) for s in ("3", r"-\tfrac12", "0.665")]).arrange(RIGHT, buff=1.4).shift(UP * 1.9)
            card = definition_card("scalar", "a single real number").next_to(nums, DOWN, buff=0.5)
            setR = VGroup(MathTex(r"\mathbb{R}", color=T.SET, font_size=60), text("= the set of all real numbers", T.SIZE_BODY, T.FG2)).arrange(RIGHT)
            elem = VGroup(MathTex(r"\in", font_size=60), text("reads “is an element of”:", T.SIZE_BODY, T.FG2),
                          MathTex(r"3\in\mathbb{R}", font_size=56)).arrange(RIGHT)
            rows = VGroup(setR, elem).arrange(DOWN, aligned_edge=LEFT, buff=0.4).next_to(card, DOWN, buff=0.5)
            self.play(FadeIn(nums, lag_ratio=0.3), FadeIn(card))
            self.play(FadeIn(setR))
            self.play(FadeIn(elem))
        self.play(FadeOut(VGroup(nums, card, rows)))

        with self.say("vector"):
            pl = plane((-1, 4), (-1, 3), 1.15).to_edge(LEFT, buff=0.8).shift(DOWN * 0.4)
            v = arrow(pl, (2, 1), T.VEC)
            tex = MathTex(r"\left(", "2", ",", "1", r"\right)", font_size=80, color=T.VEC).shift(RIGHT * 3 + UP * 1.2)
            l1 = text("1st component", T.SIZE_SMALL, T.FG2).next_to(tex, DOWN, buff=0.7).shift(LEFT * 1.3)
            l2 = text("2nd component", T.SIZE_SMALL, T.FG2).next_to(tex, DOWN, buff=0.7).shift(RIGHT * 1.3)
            p1 = Arrow(l1.get_top(), tex[1].get_bottom(), buff=0.1, color=T.FG2, stroke_width=2)
            p2 = Arrow(l2.get_top(), tex[3].get_bottom(), buff=0.1, color=T.FG2, stroke_width=2)
            self.play(Create(pl), run_time=1)
            self.play(GrowArrow(v), Write(tex))
            self.play(FadeIn(l1), FadeIn(l2), GrowArrow(p1), GrowArrow(p2))

        with self.say("dimension"):
            dim = MathTex(r"d = 2,\qquad (2,1)\in\mathbb{R}^2", font_size=48, color=T.FG).shift(RIGHT * 3 + DOWN * 1.4)
            gen = MathTex(r"\mathbb{R}^d = \{(x_1,\dots,x_d) : x_i\in\mathbb{R}\}", font_size=40, color=T.SET).next_to(dim, DOWN, buff=0.4)
            self.play(Write(dim))
            self.play(Write(gen))
        self.play(*[FadeOut(m) for m in (pl, v, tex, l1, l2, p1, p2, dim, gen)])

        with self.say("practical"):
            self.cite("radford2019gpt2", extra="numbers read from the loaded gpt2-xl config")
            m = ex["model"]
            vals = ",\\ ".join(f"{x:.2f}" for x in ex["h_plus_first6"])
            long = MathTex(r"\big(" + vals + r",\ \dots\ \big)", color=T.VEC, font_size=44).shift(UP * 0.6)
            br = Brace(long, DOWN, color=T.FG2)
            lab = MathTex(rf"d = {m['d_model']}\ \text{{components}}", font_size=40, color=T.FG).next_to(br, DOWN)
            params = text(f"GPT-2-XL: about {m['n_params'] / 1e9:.2f} billion parameters (weights), learned in training",
                          T.SIZE_SMALL, T.FG2).shift(DOWN * 2.2)
            self.play(Write(long), run_time=1.5)
            self.play(FadeIn(br), FadeIn(lab))
            self.play(FadeIn(params))
        self.wait(0.5)
