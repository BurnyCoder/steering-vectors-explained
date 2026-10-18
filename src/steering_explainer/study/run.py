"""run.py — generate, score and log every study completion (resumable JSONL).

Global context: for each prompt and seed, ONE batch holds every condition (steered α grid + random
controls), so all conditions share the prompt and the RNG stream — a paired design. Each row gets
its own vector and α through the per-row pre-hook (intervene.steering). Fluency (NLL) is measured
with the hook *removed*, i.e. under the unsteered model.
"""

import json
from pathlib import Path

import torch

from steering_explainer.config import Settings
from steering_explainer.log import get_logger
from steering_explainer.steering.intervene import completion_nll, sample, steering
from steering_explainer.steering.model import encode
from steering_explainer.steering.vectors import actadd_vector, random_like
from steering_explainer.study.design import conditions

log = get_logger(__name__)
RANDOM_SEED = 1234  # pre-registered seed for the R random control directions


def steering_and_controls(s: Settings, model, tok) -> tuple[torch.Tensor, list[torch.Tensor]]:
    """h_A plus R random directions with identical per-position norms."""
    vec = actadd_vector(model, tok, s.prompt_plus, s.prompt_minus, s.steer_layer)
    rand = [random_like(vec, torch.Generator().manual_seed(RANDOM_SEED + r)) for r in range(s.n_random)]
    return vec, rand


def _done_keys(path: Path) -> set[tuple[int, int]]:
    """(prompt_idx, seed) pairs already written, so an interrupted run resumes instead of restarting."""
    if not path.exists():
        return set()
    return {(r["prompt_idx"], r["seed"]) for r in map(json.loads, path.read_text(encoding="utf-8").splitlines())}


def run_prompts(s: Settings, model, tok, scorer, prompts: list[dict], out_path: Path) -> None:
    """Append one JSON record per (prompt, seed, condition) to `out_path`."""
    vec, rand = steering_and_controls(s, model, tok)
    conds = conditions(s)
    vecs = torch.stack([vec if c.kind == "steer" else rand[c.rand_idx] for c in conds])  # [C, n, d]
    alphas = torch.tensor([c.alpha for c in conds])  # [C]
    done = _done_keys(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("a", encoding="utf-8") as f:
        for p in prompts:
            ids = encode(tok, p["text"], s.device)
            batch = ids.repeat(len(conds), 1)  # same prompt in every row
            for seed in s.seeds:
                if (p["idx"], seed) in done:
                    continue
                g = torch.Generator(device=s.device).manual_seed(seed * 1_000_003 + p["idx"])  # unique, reproducible stream
                with steering(model, s.steer_layer, vecs, alphas):
                    out = sample(model, batch, s.max_new_tokens, s.temperature, s.top_p, s.freq_penalty, g)
                nll = completion_nll(model, out, ids.shape[1]).tolist()  # hook removed: unsteered model judges fluency
                texts = [tok.decode(o[ids.shape[1]:]) for o in out]
                pos = scorer(texts)
                for c, t, sc, nl in zip(conds, texts, pos, nll):
                    rec = {"prompt_idx": p["idx"], "label": p["label"], "prompt": p["text"], "seed": seed,
                           "condition": c.name, "kind": c.kind, "alpha": c.alpha, "rand_idx": c.rand_idx,
                           "completion": t, "p_pos": round(sc, 6), "nll": round(nl, 6)}
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    log.info("prompt %d seed %d %-12s p_pos=%.3f nll=%.3f | %r -> %r",
                             p["idx"], seed, c.name, sc, nl, p["text"], t)  # full prompt + completion logged
                f.flush()  # keep the file consistent if interrupted
