"""ch06_directions.py — directions and the linear representation hypothesis (Park et al. 2024; Mikolov et al. 2013;
caveats from Nissim et al. 2020 on analogy search and Engels et al. 2024 on non-linear, circular features).

Global context: the reason a single added vector can change behaviour. All quotes are verified
verbatim (data/sources.yaml). The 2-D word picture is explicitly labelled illustrative (toy.TOY_WORDS).
"""

from manim import DOWN, LEFT, RIGHT, UP, Create, Dot, FadeIn, FadeOut, GrowArrow, MathTex, VGroup, Write

from steering_explainer.video import theme as T
from steering_explainer.video import toy
from steering_explainer.video.widgets import ChapterScene, arrow, plane, quote_card, text


class Ch06(ChapterScene):
    CHAPTER = "ch06"

    def construct(self):
        head = self.chapter_title()
        self.play(Write(head))

        with self.say("hypothesis"):
            self.cite("park2024lrh")
            d = MathTex(r"\text{direction of } v \;=\; \hat v = v/\|v\|", font_size=44).shift(UP * 1.8)
            q = quote_card("park_lrh", width=60).shift(DOWN * 0.4)
            self.play(Write(d)); self.play(FadeIn(q))
        self.play(FadeOut(VGroup(d, q)))

        with self.say("mikolov"):
            self.cite("mikolov2013naacl", "nissim2020analogies")
            pl = plane((0, 5), (0, 4), 0.85).shift(LEFT * 3.2 + DOWN * 0.5)
            pts = {w: Dot(pl.c2p(*[float(x) for x in xy]), color=T.FG) for w, xy in toy.TOY_WORDS.items()}
            labels = VGroup(*[text(w, T.SIZE_SMALL, T.FG).next_to(pts[w], LEFT if w in ("man", "woman") else RIGHT, buff=0.1) for w in pts])
            off = lambda a, b: [float(y) - float(x) for x, y in zip(toy.TOY_WORDS[a], toy.TOY_WORDS[b])]
            g1 = arrow(pl, off("man", "woman"), T.STEER, start=toy.TOY_WORDS["man"])
            g2 = arrow(pl, off("king", "queen"), T.STEER, start=toy.TOY_WORDS["king"])
            note = text("illustrative 2-D picture, not real word vectors", T.SIZE_SMALL - 4, T.MUTED).next_to(pl, DOWN, buff=0.15)
            q = quote_card("mikolov_king_queen", width=34, size=24)
            eq = MathTex(r"\text{queen}-\text{king}\approx\text{woman}-\text{man}", font_size=34, color=T.STEER)
            # caveat: analogy searches usually exclude the input words themselves (Nissim et al. 2020, §3–4.1)
            cav = quote_card("nissim_ignore_inputs", width=40, size=20)
            right = VGroup(q, eq, cav).arrange(DOWN, buff=0.35)
            if right.height > 5.4:
                right.scale_to_fit_height(5.4)  # keep the column between the title and the footer
            right.next_to(head, DOWN, buff=0.4).set_x(3.4)
            self.play(Create(pl), FadeIn(VGroup(*pts.values(), labels)), FadeIn(note))
            self.play(GrowArrow(g1), GrowArrow(g2))
            self.play(FadeIn(q)); self.play(Write(eq)); self.play(FadeIn(cav))
        self.clear_stage(); self.add(head)

        with self.say("toy"):
            self.cite("park2024lrh", "engels2024multidim")  # a hypothesis; some features are not one-dimensional lines
            pl = plane((-1, 5), (-1, 3), 0.9).shift(LEFT * 2.5 + DOWN * 0.4)
            axis = text("→ more positive", T.SIZE_SMALL, T.PLUS).next_to(pl, DOWN, buff=0.15).align_to(pl, RIGHT)
            h = arrow(pl, (1, 2), T.VEC)
            push = arrow(pl, (2, 0), T.STEER, start=(1, 2))
            moved = arrow(pl, (3, 2), T.VEC)
            cap = VGroup(text("push along the “positive” direction", T.SIZE_SMALL, T.STEER),
                         text("a hypothesis: holds for some concepts and layers, fails for others, e.g. features that are circles, not lines:",
                              T.SIZE_SMALL, T.FG2, 34),
                         quote_card("engels_circular", width=30, size=20)
                         ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).shift(RIGHT * 3.4)
            self.play(Create(pl), FadeIn(axis), GrowArrow(h))
            self.play(GrowArrow(push), FadeIn(cap[0]))
            self.play(GrowArrow(moved), FadeIn(cap[1]), FadeIn(cap[2]))
        self.wait(0.5)
