"""toy.py — exact arithmetic for every "simplest possible" worked example in the video.

Global context: scenes never hard-code toy numbers; they call these functions, and
tests/test_toy.py pins the values the narration speaks. `Fraction` keeps the 2-D arithmetic exact
(Python docs: https://docs.python.org/3/library/fractions.html); softmax uses math.exp.
"""

import math  # exp + sqrt for softmax and norms
from fractions import Fraction  # exact rationals: 21/10 + 9/5 + 21/10 == 6 with no float error

Vec = tuple  # a toy vector is a plain tuple of numbers

A: Vec = (1, 2)  # chapter 02: first example vector a
B: Vec = (3, -1)  # chapter 02: second example vector b


def add(u: Vec, v: Vec) -> Vec:
    """Componentwise sum (u1+v1, u2+v2, ...)."""
    return tuple(x + y for x, y in zip(u, v, strict=True))  # strict: lengths must match (same ℝ^d)


def scale(c, v: Vec) -> Vec:
    """Scalar multiple c·v: multiply every component by the same number c."""
    return tuple(c * x for x in v)


def sub(u: Vec, v: Vec) -> Vec:
    """Difference u − v = u + (−1)·v: the arrow pointing from v's tip to u's tip."""
    return add(u, scale(-1, v))


def dot(u: Vec, v: Vec) -> float:
    """Dot product Σ_i u_i v_i (one number that measures alignment)."""
    return sum(x * y for x, y in zip(u, v, strict=True))


def norm(v: Vec) -> float:
    """Euclidean length ‖v‖ = sqrt(v·v)."""
    return math.sqrt(dot(v, v))


def mean(vectors: list[Vec]) -> Vec:
    """Average (1/n)·Σ v_k of n vectors, computed exactly with Fractions."""
    total = vectors[0]  # running sum starts at the first vector
    for v in vectors[1:]:
        total = add(total, v)  # Σ v_k
    return scale(Fraction(1, len(vectors)), total)  # multiply by 1/n


def softmax(z: list[float]) -> list[float]:
    """p_i = e^{z_i} / Σ_j e^{z_j}: turns any real scores into probabilities that sum to 1."""
    exps = [math.exp(x) for x in z]  # exponentiate: every score becomes positive
    total = sum(exps)  # normaliser
    return [e / total for e in exps]  # divide so they sum to 1


def vector_ops(a: Vec, b: Vec) -> dict:
    """The single combined worked example of chapter 02."""
    return {"a+b": add(a, b), "2b": scale(2, b), "a-b": sub(a, b), "a.b": dot(a, b),
            "|b|^2": dot(b, b), "|b|": norm(b)}


def residual_toy() -> dict:
    """Chapter 04: a 2-D residual stream that layers *add* updates to (pre-LN GPT-2 style)."""
    h0 = (1, 0)  # embedding of the current token
    attn_update = (0, 1)  # what the attention sublayer writes
    mlp_update = (Fraction(1, 2), Fraction(-1, 2))  # what the MLP sublayer writes
    after_attn = add(h0, attn_update)  # h0 + Attn(...)
    return {"h0": h0, "attn": attn_update, "after_attn": after_attn, "mlp": mlp_update,
            "h1": add(after_attn, mlp_update)}


# Chapter 07: (a_ℓ(p,c⁺), a_ℓ(p,c⁻)) activation pairs for three toy triples in ℝ².
TOY_TRIPLES = [
    ((Fraction("3.1"), Fraction("1.3")), (Fraction(1), Fraction(1))),
    ((Fraction("2.8"), Fraction("0.5")), (Fraction(1), Fraction(1))),
    ((Fraction("2.6"), Fraction("2.2")), (Fraction("0.5"), Fraction(2))),
]


def mean_difference(triples=TOY_TRIPLES) -> dict:
    """v = (1/|D|) Σ [a(p,c⁺) − a(p,c⁻)] — the CAA mean-difference estimator on toy data."""
    diffs = [sub(pos, neg) for pos, neg in triples]  # one difference vector per triple
    return {"diffs": diffs, "v": mean(diffs)}


def steering_toy(h: Vec = (1, 1), v: Vec = (2, 0), alpha=Fraction(3, 2)) -> dict:
    """Chapter 08: h̃ = h + α·v, then logits = W_U h̃ and softmax, for a 3-token vocabulary."""
    w_u = [(1, 0), (-1, 0), (0, 1)]  # unembedding rows for tokens " love", " hate", " the"
    h_steered = add(h, scale(alpha, v))  # the steering intervention
    logits_before = tuple(dot(row, h) for row in w_u)  # W_U h: one dot product per vocabulary row
    logits_after = tuple(dot(row, h_steered) for row in w_u)
    return {"tokens": [" love", " hate", " the"], "w_u": w_u, "h": h, "v": v, "alpha": alpha,
            "h_steered": h_steered, "logits_before": logits_before, "logits_after": logits_after,
            "p_before": softmax([float(x) for x in logits_before]),
            "p_after": softmax([float(x) for x in logits_after])}
