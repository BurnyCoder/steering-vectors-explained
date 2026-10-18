"""formulas.py — the two central equations, split into coloured parts for step-by-step building.

Global context: chapters 00 (preview), 07 (build v), 08 (apply it) and 11 (recap) all draw these,
so they live here once. Splitting MathTex into substrings lets scenes highlight one symbol at a time
(Manim docs: https://docs.manim.community/en/stable/guides/using_text.html#using-tex).
Notation follows CAA Eq. 1 (Rimsky et al. 2024) and Persona Vectors §3.2 (h ← h + α·v).
"""

from manim import MathTex, VGroup, DOWN

from steering_explainer.video import theme as T

# v_ℓ = (1/|D|) Σ_{(p,c⁺,c⁻)∈D} [ a_ℓ(p,c⁺) − a_ℓ(p,c⁻) ]
V_PARTS = [r"v_\ell", r"=", r"\frac{1}{|\mathcal{D}|}", r"\sum_{(p,\,c^+,\,c^-)\in\mathcal{D}}",
           r"\Big[", r"a_\ell(p,c^+)", r"-", r"a_\ell(p,c^-)", r"\Big]"]
V_COLORS = {0: T.STEER, 2: T.SET, 3: T.SET, 5: T.PLUS, 7: T.MINUS}

# h̃_ℓ^(t) = h_ℓ^(t) + α v_ℓ ,  t ∈ T
H_PARTS = [r"\tilde h_\ell^{(t)}", r"=", r"h_\ell^{(t)}", r"+", r"\alpha", r"\,v_\ell", r"\quad t\in T"]
H_COLORS = {0: T.VEC, 2: T.VEC, 4: T.ALPHA, 5: T.STEER, 6: T.SET}

# context line: where h lives (GPT-2 block, LayerNorm omitted as in Arditi et al. 2024 Eq. 1) and the readout
CONTEXT = r"h_{\ell+1}=h_\ell+\mathrm{Attn}_\ell(h_\ell)+\mathrm{MLP}_\ell\big(h_\ell+\mathrm{Attn}_\ell(h_\ell)\big),\qquad p=\mathrm{softmax}(W_U h_L)"


def colored(parts: list[str], colors: dict, size: int = 46) -> MathTex:
    tex = MathTex(*parts, font_size=size, color=T.FG)
    for i, c in colors.items():
        tex[i].set_color(c)
    return tex


def v_equation(size: int = 46) -> MathTex:
    return colored(V_PARTS, V_COLORS, size)


def h_equation(size: int = 46) -> MathTex:
    return colored(H_PARTS, H_COLORS, size)


def full_objects(size: int = 46) -> VGroup:
    """Both equations stacked, with the context line underneath (smaller, muted)."""
    ctx = MathTex(CONTEXT, font_size=size * 0.55, color=T.FG2)
    return VGroup(v_equation(size), h_equation(size), ctx).arrange(DOWN, buff=0.6)
