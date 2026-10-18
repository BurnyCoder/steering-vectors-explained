"""ch00_hook.py — cold open: a real unsteered vs. steered GPT-2-XL continuation, then the full equations.

Global context: the completions come from data/practical_example.json (seed 0 — the first sample,
not cherry-picked); the equations come from video/formulas.py and are fully explained in ch01-ch11.
"""

from manim import DOWN, UP, LEFT, FadeIn, FadeOut, Write, Brace, MathTex, VGroup, SurroundingRectangle

from steering_explainer.video import theme as T
from steering_explainer.video.formulas import full_objects
from steering_explainer.video.widgets import ChapterScene, example, text


def _clean(s: str) -> str:
    return " ".join(s.split())  # completions may contain newlines; show them on one flowing paragraph


class Ch00(ChapterScene):
    CHAPTER = "ch00"

    def construct(self):
        ex = example()
        c0 = ex["completions"][0]  # seed 0
        title = text("Steering vectors, from scratch", T.SIZE_TITLE + 8, T.FG, weight="BOLD")
        self.play(Write(title), run_time=1.2)
        self.play(title.animate.scale(0.6).to_edge(UP, buff=0.3))

        with self.say("intro"):
            prompt = text(f"“{ex['prompt']}”", T.SIZE_BODY, T.FG, weight="BOLD").shift(UP * 2)
            tag0 = text("GPT-2-XL, unchanged:", T.SIZE_SMALL, T.FG2).next_to(prompt, DOWN, buff=0.45).to_edge(LEFT, buff=1)
            out0 = text("…" + _clean(c0["unsteered"]), T.SIZE_SMALL, T.FG, width=70).next_to(tag0, DOWN, aligned_edge=LEFT)
            self.play(FadeIn(prompt))
            self.play(FadeIn(tag0), Write(out0), run_time=3)

        with self.say("steered"):
            self.cite("turner2023lw", extra=f"our run: GPT-2-XL, layer {ex['layer']}, coefficient +{ex['coeff']:g}, seed 0")
            tag1 = text("same model, same random choices, + one list of numbers added inside:", T.SIZE_SMALL, T.PLUS)
            tag1.next_to(out0, DOWN, buff=0.5).align_to(tag0, LEFT)
            out1 = text("…" + _clean(c0["steered"]), T.SIZE_SMALL, T.FG, width=70).next_to(tag1, DOWN, aligned_edge=LEFT)
            self.play(FadeIn(tag1))
            self.play(Write(out1), run_time=3)

        with self.say("name"):
            nums = MathTex(r"\big(" + ",\\ ".join(f"{x:.2f}" for x in ex["h_A_first6"]) + r",\ \dots\big)",
                           color=T.STEER, font_size=48).shift(DOWN * 0.6)
            brace = Brace(nums, UP, color=T.FG2)
            lab = text("a list of numbers = a vector  →  here: a steering vector", T.SIZE_BODY, T.STEER).next_to(brace, UP, buff=0.15)
            self.play(FadeOut(VGroup(tag0, tag1, out0, out1)))
            self.play(Write(nums), FadeIn(brace), FadeIn(lab))

        with self.say("objects"):
            self.uncite()
            self.play(*[FadeOut(m) for m in (prompt, nums, brace, lab)])
            eqs = full_objects(50).move_to(DOWN * 0.2)
            self.play(Write(eqs[0]), run_time=2.5)
            self.play(Write(eqs[1]), run_time=2)
            self.play(FadeIn(eqs[2]))
            self.play(FadeIn(SurroundingRectangle(eqs, color=T.MUTED, buff=0.35, corner_radius=0.15)))
        self.wait(0.5)
