"""prompts.py — deterministic IMDb review prefixes for the study (pilot and main sets are disjoint).

Global context: prefixes of real movie reviews (Maas et al. 2011, HF `stanfordnlp/imdb`) are text
unrelated to the "Love"/"Hate" contrast prompts, so the vector is never built from evaluation data.
Alternating negative/positive reviews keeps the unsteered baseline away from 0 and 1 (no ceiling/floor).
Docs: datasets.load_dataset / Dataset.shuffle(seed=...) (https://huggingface.co/docs/datasets).
"""

import re

from datasets import load_dataset


def imdb_prefixes(n_total: int, n_words: int, seed: int = 0) -> list[dict]:
    """First `n_total` prompts: [{"idx", "label", "text"}], alternating neg/pos, each `n_words` words."""
    ds = load_dataset("stanfordnlp/imdb", split="test").shuffle(seed=seed)  # 25k labelled reviews, fixed order
    by_label = {0: [], 1: []}  # 0 = negative, 1 = positive review
    for row in ds:
        if len(by_label[0]) >= n_total and len(by_label[1]) >= n_total:
            break
        by_label[row["label"]].append(row["text"])
    out = []
    for i in range(n_total):
        label = i % 2  # alternate: neg, pos, neg, ...
        text = re.sub(r"<br\s*/?>", " ", by_label[label][i // 2])  # strip HTML line breaks
        words = text.split()[:n_words]  # keep the first n words
        out.append({"idx": i, "label": label, "text": " ".join(words)})
    return out
