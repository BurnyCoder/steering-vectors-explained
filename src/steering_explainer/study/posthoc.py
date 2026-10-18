"""posthoc.py — exploratory (NOT pre-registered) analyses, kept separate from the confirmatory ones.

Global context: after experiment 02, reading completions showed that α = −5 makes GPT-2-XL write the
literal word "hate" rather than negative text. This module quantifies that observation: the share
of completions containing "love"/"hate" word forms per condition, with 95% bootstrap CIs over
prompts, plus how positive the classifier rates the α = −5 completions that contain "hate".
Results go to data/study/<run>_posthoc.json and are always labelled post-hoc.
v1.0 matched the substrings `lov` / `hat(e|ing|red)`, which also counted "glove", "whatever" and "chateau";
the fact-check (docs/fact_check.md) replaced them with whole-word patterns (\\b = word boundary,
https://docs.python.org/3/library/re.html#regular-expression-syntax).
"""

import json
from pathlib import Path

import pandas as pd

from steering_explainer.config import Settings
from steering_explainer.study import stats

PATTERNS = {"love": r"\blov(?:e|es|ed|ing|er|ers)\b",  # love, loves, loved, loving, lover(s) — not "lovely"/"glove"
            "hate": r"\bhat(?:e|es|ed|ing|red|eful)\b"}  # hate(s/d), hating, hatred, hateful — not "whatever"/"hat"


def mentions(texts, word: str) -> list[bool]:
    """For each text: does it contain a whole-word form of `word` (case-insensitive)?"""
    return pd.Series(list(texts), dtype=str).str.contains(PATTERNS[word], case=False, regex=True).tolist()


def lexical_rates(s: Settings, records: Path) -> dict:
    """{condition: {word: [mean, lo, hi]}}: share of completions containing each word form, CI over prompts."""
    df = pd.read_json(records, lines=True)
    out = {}
    for word in PATTERNS:
        df[word] = pd.Series(mentions(df.completion, word), index=df.index).astype(float)
    for (kind, alpha), g in df.groupby(["kind", "alpha"]):
        per_prompt = g.groupby("prompt_idx")[list(PATTERNS)].mean()  # average over seeds (and random directions)
        out[f"{kind}_{alpha:g}"] = {w: list(stats.paired_bootstrap_ci(per_prompt[w], s.bootstrap_resamples, seed=0))
                                    for w in PATTERNS}
    steer = df[df.kind == "steer"]
    hate5 = steer[(steer.alpha == -5) & (steer.hate > 0)]  # α = −5 completions that say "hate"
    return {"label": "post-hoc, exploratory (not pre-registered)", "patterns": PATTERNS, "rates": out,
            "hate_at_minus5_n": int(len(hate5)), "hate_at_minus5_positivity": float(hate5.p_pos.mean()),
            "unsteered_positivity": float(steer[steer.alpha == 0].p_pos.mean())}


def write_posthoc(s: Settings) -> None:
    d = s.data_dir / "study"
    for run in ("main", "exp02"):
        res = lexical_rates(s, d / f"{run}.jsonl")
        (d / f"{run}_posthoc.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
