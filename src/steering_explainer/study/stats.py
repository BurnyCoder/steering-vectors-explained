"""stats.py — paired bootstrap CIs, Wilcoxon + Holm, power analysis, per-prompt Spearman.

Global context: the study is *paired by prompt* (every condition sees the same prompts and seeds),
so all tests operate on per-prompt differences.
Sources: percentile bootstrap (Efron & Tibshirani 1993); Holm (1979) step-down correction via
statsmodels.stats.multitest.multipletests(method="holm")
(https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html);
power for a one-sample/paired t-test via statsmodels TTestPower.solve_power
(https://www.statsmodels.org/stable/generated/statsmodels.stats.power.TTestPower.solve_power.html);
scipy.stats.wilcoxon / spearmanr (https://docs.scipy.org/doc/scipy/reference/stats.html).
"""

import math

import numpy as np
from scipy import stats as sps
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.power import TTestPower


def paired_bootstrap_ci(diffs, n_boot: int = 10_000, seed: int = 0, ci: float = 0.95) -> tuple[float, float, float]:
    """(mean, lower, upper) percentile-bootstrap CI of the mean of per-prompt differences."""
    x = np.asarray(diffs, dtype=float)
    rng = np.random.default_rng(seed)  # seeded -> reproducible CIs
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))  # resample prompts with replacement
    boots = x[idx].mean(axis=1)  # bootstrap distribution of the mean
    tail = (1 - ci) / 2 * 100
    lo, hi = np.percentile(boots, [tail, 100 - tail])
    return float(x.mean()), float(lo), float(hi)


def wilcoxon_p(diffs, alternative: str = "two-sided") -> float:
    """Wilcoxon signed-rank p-value for H0: median difference = 0 (1.0 if all differences are 0)."""
    x = np.asarray(diffs, dtype=float)
    if np.allclose(x, 0):
        return 1.0
    return float(sps.wilcoxon(x, alternative=alternative).pvalue)


def holm(pvals) -> list[float]:
    """Holm-adjusted p-values (family-wise error control)."""
    return [float(p) for p in multipletests(list(pvals), method="holm")[1]]


def required_n(effect_size_dz: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Prompts needed to detect a standardized paired effect d_z with a two-sided paired t-test."""
    n = TTestPower().solve_power(effect_size=abs(effect_size_dz), alpha=alpha, power=power, alternative="two-sided")
    return int(math.ceil(n))


def cohens_dz(diffs) -> float:
    """Standardized paired effect d_z = mean(diff) / sd(diff)."""
    x = np.asarray(diffs, dtype=float)
    return float(x.mean() / x.std(ddof=1)) if x.std(ddof=1) > 0 else float("inf")


def per_unit_spearman(alphas, rows) -> np.ndarray:
    """Spearman ρ between α and the outcome, computed separately for every prompt (row)."""
    return np.array([sps.spearmanr(alphas, r).statistic for r in np.asarray(rows, dtype=float)])
