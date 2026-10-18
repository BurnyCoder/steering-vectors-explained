"""posthoc.py — exploratory (NOT pre-registered) analyses, kept separate from the confirmatory ones.

Global context: after experiment 02, reading completions showed that α = −5 makes GPT-2-XL write the
literal word "hate" rather than negative text. This module quantifies that observation: the share
of completions containing "love"/"hate" word forms per condition, with 95% bootstrap CIs over
prompts. Results go to data/study/<run>_posthoc.json and are always labelled post-hoc.
"""

import json
from pathlib import Path

import pandas as pd

from steering_explainer.config import Settings
from steering_explainer.study import stats

PATTERNS = {"love": r"lov", "hate": r"hat(?:e|ing|red)"}  # love/loving/lovely…; hate/hating/hatred (case-insensitive)


def lexical_rates(s: Settings, records: Path) -> dict:
    """{condition: {word: [mean, lo, hi]}}: share of completions containing each word form, CI over prompts."""
    df = pd.read_json(records, lines=True)
    out = {}
    for word, pat in PATTERNS.items():
        df[word] = df.completion.str.contains(pat, case=False, regex=True).astype(float)
    for (kind, alpha), g in df.groupby(["kind", "alpha"]):
        per_prompt = g.groupby("prompt_idx")[list(PATTERNS)].mean()  # average over seeds (and random directions)
        out[f"{kind}_{alpha:g}"] = {w: list(stats.paired_bootstrap_ci(per_prompt[w], s.bootstrap_resamples, seed=0))
                                    for w in PATTERNS}
    return {"label": "post-hoc, exploratory (not pre-registered)", "patterns": PATTERNS, "rates": out}


def write_posthoc(s: Settings) -> None:
    d = s.data_dir / "study"
    for run in ("main", "exp02"):
        res = lexical_rates(s, d / f"{run}.jsonl")
        (d / f"{run}_posthoc.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
