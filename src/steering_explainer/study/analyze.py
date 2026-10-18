"""analyze.py — the pre-registered analysis (reports/exp01_preregistration.md) on the JSONL records.

Global context: records -> per-prompt means (averaged over seeds, and over the R random directions)
-> paired differences -> bootstrap CIs / Wilcoxon+Holm / per-prompt Spearman -> summary.json,
consumed by the report, the paper and chapter 09 of the video.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from steering_explainer.config import Settings
from steering_explainer.study import stats
from steering_explainer.study.design import PRIMARY_ALPHA


def load_records(path: Path) -> pd.DataFrame:
    """One row per (prompt, seed, condition)."""
    return pd.read_json(path, lines=True)


def per_prompt(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Rows = prompts; columns = (kind, alpha); values = mean metric over seeds (and random directions)."""
    return df.groupby(["prompt_idx", "kind", "alpha"])[metric].mean().unstack(["kind", "alpha"])


def primary_diff(df: pd.DataFrame, ref: tuple = ("random", PRIMARY_ALPHA)) -> np.ndarray:
    """Per-prompt P_pos(steer, α=5) − P_pos(ref): exp01 ref = random(5), exp02 ref = steer(0)."""
    t = per_prompt(df, "p_pos")
    return (t[("steer", PRIMARY_ALPHA)] - t[ref]).to_numpy()


def _ci(x, s: Settings) -> list[float]:
    return list(stats.paired_bootstrap_ci(x, s.bootstrap_resamples, seed=0))


def analyze(s: Settings, records: Path, ref: tuple = ("random", PRIMARY_ALPHA)) -> dict:
    df = load_records(records)
    pp, nll = per_prompt(df, "p_pos"), per_prompt(df, "nll")
    out = {"n_prompts": int(pp.shape[0]), "n_completions": int(len(df)), "seeds": list(s.seeds)}

    # condition means with CIs (for the dose-response figure)
    out["means"] = {m: {f"{k}_{a:g}": _ci(tab[(k, a)], s) for (k, a) in tab.columns}
                    for m, tab in (("p_pos", pp), ("nll", nll))}

    # H1 primary
    d = primary_diff(df, ref)
    m, lo, hi = _ci(d, s)
    out["primary"] = {"contrast": f"P_pos(steer,5) - P_pos({ref[0]},{ref[1]:g})", "mean": m, "lo": lo, "hi": hi,
                      "dz": stats.cohens_dz(d), "verdict": "supported" if lo > 0 else "falsified"}

    # H2 dose-response: per-prompt Spearman over the steered α grid
    alphas = sorted(a for k, a in pp.columns if k == "steer")
    rho = stats.per_unit_spearman(alphas, pp[[("steer", a) for a in alphas]].to_numpy())
    rho = rho[~np.isnan(rho)]  # constant rows have undefined ρ
    rm, rlo, rhi = _ci(rho, s)
    out["h2_spearman"] = {"mean_rho": rm, "lo": rlo, "hi": rhi, "n_defined": int(len(rho)),
                          "verdict": "supported" if rlo > 0 else "falsified"}

    # secondary family: steer(α) − steer(0) for α ≠ 0, and steer(15) − random(15); Holm-corrected Wilcoxon
    tests = [(f"steer_{a:g} - steer_0", pp[("steer", a)] - pp[("steer", 0.0)]) for a in alphas if a != 0]
    top = max(s.random_alphas)
    tests.append((f"steer_{top:g} - random_{top:g}", pp[("steer", top)] - pp[("random", top)]))
    p_raw = [stats.wilcoxon_p(x) for _, x in tests]
    out["secondary"] = [{"contrast": n, **dict(zip(("mean", "lo", "hi"), _ci(x, s))), "p_raw": p, "p_holm": ph}
                        for (n, x), p, ph in zip(tests, p_raw, stats.holm(p_raw))]
    h3 = next(t for t in out["secondary"] if t["contrast"].startswith("steer_-"))
    out["h3_sign"] = {**h3, "verdict": "supported" if (h3["mean"] < 0 and h3["p_holm"] < 0.05) else "falsified"}

    # H4 fluency cost: NLL(condition) − NLL(steer_0)
    base = nll[("steer", 0.0)]
    out["fluency"] = {f"{k}_{a:g}": dict(zip(("mean", "lo", "hi"), _ci(nll[(k, a)] - base, s)))
                      for (k, a) in nll.columns if not (k == "steer" and a == 0)}

    # robustness: primary contrast per seed
    out["primary_per_seed"] = {int(sd): dict(zip(("mean", "lo", "hi"), _ci(primary_diff(g, ref), s)))
                               for sd, g in df.groupby("seed")}

    # non-cherry-picked examples: the first three prompts, seed 0, α = 0 vs α = 5
    ex = df[(df.seed == s.seeds[0]) & (df.kind == "steer") & df.alpha.isin([0.0, PRIMARY_ALPHA])]
    out["examples"] = [{"prompt": g.prompt.iloc[0], **{f"alpha_{a:g}": g[g.alpha == a].completion.iloc[0] for a in (0.0, PRIMARY_ALPHA)}}
                       for _, g in list(ex.groupby("prompt_idx"))[:3]]
    return out


def write_summary(summary: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
