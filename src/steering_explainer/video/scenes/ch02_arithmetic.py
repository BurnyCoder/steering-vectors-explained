"""ch02_arithmetic.py — addition, scalar multiple, subtraction, Σ and mean, dot product, norm, unit vector.

Global context: one combined worked example a = (1, 2), b = (3, −1); every number shown is computed
by video/toy.py (tests/test_toy.py pins them). Subtraction and the mean are exactly the operations
the steering vector uses in chapter 07; the dot product returns as logits in chapter 05.
"""

from manim import DOWN, LEFT, RIGHT, UP, Create, FadeIn, FadeOut, GrowArrow, MathTex, ReplacementTransform, Write

from steering_explainer.video import theme as T
from steering_explainer.video import toy
from steering_explainer.video.widgets import ChapterScene, EqColumn, arrow, num, plane, tip_label, tup

FS = 38  # equation font size in this chapter


class Ch02(ChapterScene):
    CHAPTER = "ch02"

    def construct(self):
        r = toy.vector_ops(toy.A, toy.B)
        head = self.chapter_title()
        self.play(Write(head))
        pl = plane((-3, 7), (-3, 4), 0.6).to_edge(LEFT, buff=0.4).shift(DOWN * 0.45)
        self.play(Create(pl), run_time=0.8)
        col = EqColumn()

        with self.say("add"):
            a, b = arrow(pl, toy.A, T.VEC), arrow(pl, toy.B, T.STEER)
            la, lb = tip_label(a, "a", T.VEC, LEFT), tip_label(b, "b", T.STEER, DOWN)
            eq = col.place(MathTex(r"a=" + tup(toy.A), r",\quad ", r"b=" + tup(toy.B), font_size=FS))
            eq[0].set_color(T.VEC); eq[2].set_color(T.STEER)
            self.play(GrowArrow(a), GrowArrow(b), FadeIn(la), FadeIn(lb), Write(eq))
            b_copy, b_moved = b.copy(), arrow(pl, toy.B, T.STEER, start=toy.A)  # tail of b at the tip of a
            s = arrow(pl, r["a+b"], T.PLUS)
            add = col.place(MathTex(r"a+b=(1+3,\ 2-1)=", tup(r["a+b"]), font_size=FS))
            add[1].set_color(T.PLUS)
            self.play(ReplacementTransform(b_copy, b_moved))
            self.play(GrowArrow(s), FadeIn(tip_label(s, "a+b", T.PLUS, RIGHT)), Write(add))

        with self.say("scale"):
            two_b = arrow(pl, r["2b"], T.ALPHA)
            sc = col.place(MathTex(r"2b=(2\cdot3,\ 2\cdot(-1))=", tup(r["2b"]), font_size=FS))
            sc[1].set_color(T.ALPHA)
            neg = col.place(MathTex(r"(-1)\,b=" + tup(toy.scale(-1, toy.B)) + r"\ \ \text{(flipped)}", font_size=FS - 4, color=T.FG2))
            flip = arrow(pl, toy.scale(-1, toy.B), T.FG2)
            lab2b = tip_label(two_b, "2b", T.ALPHA, DOWN)
            self.play(GrowArrow(two_b), FadeIn(lab2b), Write(sc))
            self.play(GrowArrow(flip), Write(neg))

        with self.say("sub"):
            d = arrow(pl, r["a-b"], T.MINUS, start=toy.B)  # from the tip of b to the tip of a
            sb = col.place(MathTex(r"a-b=a+(-1)\,b=", tup(r["a-b"]), font_size=FS))
            sb[1].set_color(T.MINUS)
            self.play(FadeOut(two_b), FadeOut(lab2b), FadeOut(flip), GrowArrow(d), Write(sb))
            self.play(FadeIn(MathTex("a-b", color=T.MINUS, font_size=32).next_to(d.get_center(), RIGHT, buff=0.15)))
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (head, pl, self.footer)])
        col = EqColumn()

        with self.say("sum_mean"):
            sig = col.place(MathTex(r"\sum_{k=1}^{n} x_k = x_1 + x_2 + \dots + x_n", font_size=FS + 4))
            mean = col.place(MathTex(r"\text{mean}=\frac{1}{n}\sum_{k=1}^{n} x_k", font_size=FS + 4))
            m = toy.mean([(1, 2), (3, 4)])
            ex = col.place(MathTex(r"\tfrac12\big[(1,2)+(3,4)\big]=", tup(m), font_size=FS))
            ex[1].set_color(T.PLUS)
            p1, p2, pm = arrow(pl, (1, 2), T.FG2), arrow(pl, (3, 4), T.FG2), arrow(pl, m, T.PLUS)
            self.play(Write(sig)); self.play(Write(mean))
            self.play(GrowArrow(p1), GrowArrow(p2), Write(ex)); self.play(GrowArrow(pm))
        self.play(*[FadeOut(m_) for m_ in self.mobjects if m_ not in (head, pl, self.footer)])
        col = EqColumn()

        with self.say("dot_norm"):
            a, b = arrow(pl, toy.A, T.VEC), arrow(pl, toy.B, T.STEER)
            dot = col.place(MathTex(r"a\cdot b=1\cdot3+2\cdot(-1)=", num(r["a.b"]), font_size=FS))
            dot[1].set_color(T.ALPHA)
            nrm = col.place(MathTex(r"\|b\|=\sqrt{b\cdot b}=\sqrt{3^2+(-1)^2}", font_size=FS))
            nrm2 = col.place(MathTex(r"=\sqrt{" + num(r["|b|^2"]) + r"}\approx", f"{r['|b|']:.2f}", font_size=FS))
            nrm2[1].set_color(T.ALPHA)
            unit = col.place(MathTex(r"\hat b=\frac{b}{\|b\|}\approx" + tup([x / r["|b|"] for x in toy.B], 2) + r",\quad \|\hat b\|=1", font_size=FS))
            ub = arrow(pl, [x / r["|b|"] for x in toy.B], T.PLUS)
            ub.set_stroke(width=9)
            self.play(GrowArrow(a), GrowArrow(b), Write(dot))
            self.play(Write(nrm)); self.play(Write(nrm2))
            self.play(b.animate.set_opacity(0.35), GrowArrow(ub), FadeIn(tip_label(ub, r"\hat b", T.PLUS, DOWN)), Write(unit))
        self.wait(0.5)
