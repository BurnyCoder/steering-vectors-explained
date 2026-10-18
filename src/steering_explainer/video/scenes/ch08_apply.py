"""ch08_apply.py — the intervention h̃ = h + α·v, the edited positions T, a toy readout, and real GPT-2-XL output.

Global context: builds equation (2) and connects it to chapter 05's readout: the toy uses the same
3-token unembedding (video/toy.py steering_toy); the real probabilities/completions come from
practical_example.json (seed 0 = first sample, not cherry-picked).
"""

from manim import (DOWN, LEFT, RIGHT, UP, Brace, Create, FadeIn, FadeOut, GrowArrow, MathTex, SurroundingRectangle,
                   VGroup, Write)

from steering_explainer.video import theme as T
from steering_explainer.video import toy
from steering_explainer.video.formulas import h_equation
from steering_explainer.video.widgets import (ChapterScene, arrow, example, num, plane, prob_bars, quote_card, text,
                                              token_row, tup)


def _clean(s: str) -> str:
    return " ".join(s.split())


class Ch08(ChapterScene):
    CHAPTER = "ch08"

    def construct(self):
        ex = example()
        head = self.chapter_title()
        self.play(Write(head))

        with self.say("formula"):
            self.cite("turner2024actadd", "chen2025persona")
            eq = h_equation(58).shift(UP * 1.2)
            self.play(Write(eq[2]))
            for idx, label, side in (((4,), "α ∈ ℝ: steering coefficient (strength and sign)", DOWN),
                                     ((5,), "v: the steering vector", UP), ((0,), "h̃: steered activation", DOWN)):
                part = VGroup(*[eq[i] for i in idx])
                self.play(Write(part), *([Write(eq[3])] if idx == (4,) else []), *([Write(eq[1])] if idx == (0,) else []))
                b = Brace(part, side, color=T.FG2)
                t = text(label, T.SIZE_SMALL, T.FG2).next_to(b, side, buff=0.1)
                self.play(FadeIn(b), FadeIn(t)); self.wait(0.2); self.play(FadeOut(b), FadeOut(t))
            frozen = text("weights unchanged — only activations are edited", T.SIZE_SMALL, T.PLUS).next_to(eq, DOWN, buff=0.5)
            q = quote_card("actadd_bias_terms", width=70, size=22).to_edge(DOWN, buff=0.6)
            self.play(FadeIn(frozen)); self.play(FadeIn(q))
        self.play(FadeOut(VGroup(frozen, q)))

        with self.say("positions"):
            self.cite("turner2024actadd", "panickssery2024caa")
            self.play(Write(eq[6]))
            row = token_row(ex["tokens_prompt"] + ["…", "…"], T.FG, 24).shift(DOWN * 0.4)
            n = len(ex["tokens_plus"])  # ActAdd edits the first n positions
            act = SurroundingRectangle(VGroup(*row[:n]), color=T.STEER, buff=0.08)
            act_l = VGroup(text("ActAdd: front positions 0…n−1,", T.SIZE_SMALL, T.STEER),  # a different vector per position
                           MathTex(r"v^{(t)} = h_A^{(t)}\ \text{(row } t \text{ of } h_A)", font_size=30, color=T.STEER)
                           ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).next_to(act, DOWN, buff=0.2).align_to(act, LEFT)
            caa = SurroundingRectangle(VGroup(*row[len(ex["tokens_prompt"]):]), color=T.ALPHA, buff=0.08)
            caa_l = text("CAA: every position after the prompt", T.SIZE_SMALL, T.ALPHA).next_to(caa, UP, buff=0.2).align_to(caa, RIGHT)
            q = quote_card("caa_positions", width=70, size=22).to_edge(DOWN, buff=0.6)
            self.play(FadeIn(row)); self.play(Create(act), FadeIn(act_l)); self.play(Create(caa), FadeIn(caa_l)); self.play(FadeIn(q))
        self.clear_stage(); self.add(head)

        with self.say("toy"):
            st = toy.steering_toy()
            pl = plane((-1, 5), (-1, 2), 0.75).to_edge(LEFT, buff=0.5).shift(DOWN * 0.3)
            h = arrow(pl, st["h"], T.VEC)
            av = arrow(pl, toy.scale(st["alpha"], st["v"]), T.STEER, start=st["h"])
            hs = arrow(pl, st["h_steered"], T.ALPHA)
            calc = MathTex(r"\tilde h=" + tup(st["h"]) + r"+" + num(st["alpha"]) + r"\cdot" + tup(st["v"]) + "=" + tup(st["h_steered"]),
                           font_size=38).to_edge(UP, buff=1.3).shift(RIGHT * 2.2)
            rows = ",\\ ".join(rf"\text{{{tk.strip()}}}\,{tup(w)}" for tk, w in zip(st["tokens"], st["w_u"]))
            wu = MathTex(r"W_U\ \text{rows: }" + rows, font_size=30, color=T.FG2).next_to(calc, DOWN, buff=0.25)
            toy_note = text("toy: treat h̃ as the final stream", T.SIZE_SMALL - 4, T.MUTED).next_to(pl, DOWN, buff=0.2)
            lg = MathTex(r"z = W_U\tilde h: " + tup(st["logits_before"]) + r"\ \to\ " + tup(st["logits_after"]),
                         font_size=38).next_to(wu, DOWN, buff=0.25)
            before = prob_bars(st["tokens"], st["p_before"], T.VEC, 2.6)
            after = prob_bars(st["tokens"], st["p_after"], T.ALPHA, 2.6)
            bars = VGroup(VGroup(text("before", T.SIZE_SMALL, T.FG2), before).arrange(DOWN, aligned_edge=LEFT),
                          VGroup(text("after", T.SIZE_SMALL, T.FG2), after).arrange(DOWN, aligned_edge=LEFT)
                          ).arrange(RIGHT, buff=0.8).next_to(lg, DOWN, buff=0.5)
            self.play(Create(pl), GrowArrow(h))
            self.play(GrowArrow(av), Write(calc), FadeIn(toy_note))
            self.play(GrowArrow(hs), FadeIn(wu), Write(lg))
            self.play(FadeIn(bars, lag_ratio=0.3))
        self.clear_stage(); self.add(head)

        with self.say("real"):
            self.cite("turner2023lw", extra="our run, seed 0")
            setup = quote_card("lw_love_hate_setup", width=70, size=24).to_edge(UP, buff=1.2)
            gains = ex["next_token"]["largest_gains"][:3]
            g = prob_bars([t for t, _ in gains], [q for _, q in gains], T.PLUS, 20, signed=True)
            g_l = text(f"largest next-token probability gains after “{ex['prompt']}” (α = +{ex['coeff']:g} vs 0)", T.SIZE_SMALL, T.FG2)
            gv = VGroup(g_l, g).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(setup, DOWN, buff=0.5)
            self.play(FadeIn(setup)); self.play(FadeIn(gv))
            self.wait_until_bookmark("cont")
            self.play(FadeOut(gv))
            c0 = ex["completions"][0]
            cols = VGroup(VGroup(text("α = 0 (unsteered)", T.SIZE_SMALL, T.FG2), text("…" + _clean(c0["unsteered"]), T.SIZE_SMALL - 2, T.FG, 42)).arrange(DOWN, aligned_edge=LEFT),
                          VGroup(text(f"α = +{ex['coeff']:g} (steered)", T.SIZE_SMALL, T.STEER), text("…" + _clean(c0["steered"]), T.SIZE_SMALL - 2, T.FG, 42)).arrange(DOWN, aligned_edge=LEFT)
                          ).arrange(RIGHT, buff=0.7, aligned_edge=UP).next_to(setup, DOWN, buff=0.45)
            if cols.width > 13:
                cols.scale_to_fit_width(13)
            note = quote_card("lw_cherry_picked", width=90, size=20).to_edge(DOWN, buff=0.6)
            self.play(FadeIn(cols))
            self.wait_until_bookmark("note")
            self.play(FadeIn(note))
        self.wait(0.5)
