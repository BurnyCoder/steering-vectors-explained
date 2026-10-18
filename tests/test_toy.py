"""test_toy.py — the worked examples shown on screen are computed, so test the computations.

Global context: video/toy.py is the only place on-screen toy numbers come from; these tests pin
the exact values the narration speaks (e.g. softmax(2,1,0) = 0.665, 0.245, 0.090).
"""

from fractions import Fraction  # exact rational arithmetic for the toy vectors

import pytest  # approx() for float comparisons

from steering_explainer.video import toy  # module under test


def test_vector_operations_combined_example():
    r = toy.vector_ops(toy.A, toy.B)  # a=(1,2), b=(3,-1) from chapter 02
    assert r["a+b"] == (4, 1)  # componentwise addition
    assert r["2b"] == (6, -2)  # scalar multiplication
    assert r["a-b"] == (-2, 3)  # subtraction = a + (-1)b
    assert r["a.b"] == 1  # 1*3 + 2*(-1)
    assert r["|b|^2"] == 10  # squared norm, so |b| = sqrt(10)
    assert r["|b|"] == pytest.approx(10 ** 0.5)  # 3.1623


def test_mean_of_vectors():
    assert toy.mean([(1, 2), (3, 4)]) == (2, 3)  # average of two vectors


def test_softmax_matches_narration():
    p = toy.softmax([2, 1, 0])  # chapter 05 example
    assert [round(x, 3) for x in p] == [0.665, 0.245, 0.090]
    assert sum(p) == pytest.approx(1.0)  # a probability distribution


def test_residual_stream_toy():
    s = toy.residual_toy()  # h0 + attention update + MLP update
    assert s["h0"] == (1, 0) and s["after_attn"] == (1, 1) and s["h1"] == (Fraction(3, 2), Fraction(1, 2))


def test_mean_difference_cancels_noise():
    m = toy.mean_difference(toy.TOY_TRIPLES)  # three noisy 2-D differences
    assert m["diffs"] == [(Fraction(21, 10), Fraction(3, 10)), (Fraction(9, 5), Fraction(-1, 2)), (Fraction(21, 10), Fraction(1, 5))]
    assert m["v"] == (2, 0)  # the irrelevant 2nd coordinate averages to exactly 0


def test_steering_toy_shifts_probabilities():
    s = toy.steering_toy()  # h=(1,1), v=(2,0), alpha=1.5, 3-token vocabulary
    assert s["h_steered"] == (4, 1)
    assert s["logits_before"] == (1, -1, 1) and s["logits_after"] == (4, -4, 1)
    assert [round(x, 3) for x in s["p_before"]] == [0.468, 0.063, 0.468]
    assert [round(x, 3) for x in s["p_after"]] == [0.952, 0.0, 0.047]
