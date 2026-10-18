"""test_stats.py — sanity checks for the pre-registered analysis primitives (no model needed)."""

import numpy as np
import pytest

from steering_explainer.study import stats


def test_bootstrap_ci_covers_true_mean_and_is_ordered():
    rng = np.random.default_rng(0)
    x = rng.normal(0.3, 1.0, size=400)  # paired differences with true mean 0.3
    m, lo, hi = stats.paired_bootstrap_ci(x, n_boot=4000, seed=1)
    assert lo < m < hi and lo < 0.3 < hi
    assert m == pytest.approx(x.mean())


def test_bootstrap_is_reproducible_with_seed():
    x = np.arange(10.0)
    assert stats.paired_bootstrap_ci(x, 2000, seed=5) == stats.paired_bootstrap_ci(x, 2000, seed=5)


def test_holm_adjustment_matches_definition():
    adj = stats.holm([0.01, 0.04, 0.03])  # sorted: .01*3=.03, .03*2=.06, max(.06,.04*1)=.06
    assert adj == pytest.approx([0.03, 0.06, 0.06])


def test_required_n_shrinks_with_effect_size():
    assert stats.required_n(0.2, 0.05, 0.8) > stats.required_n(0.5, 0.05, 0.8) > 10


def test_per_unit_spearman_detects_monotone_dose_response():
    alphas = [-5, 0, 2, 5, 10, 15]
    rows = np.array([[0.1, 0.2, 0.3, 0.4, 0.6, 0.7], [0.2, 0.1, 0.3, 0.5, 0.5, 0.9]])
    rho = stats.per_unit_spearman(alphas, rows)
    assert rho[0] == pytest.approx(1.0) and 0.8 < rho[1] < 1.0
