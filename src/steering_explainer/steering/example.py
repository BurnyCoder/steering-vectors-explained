"""example.py — the video's *practical* worked example: ActAdd "Love" − "Hate" on GPT-2-XL.

Global context: every real number shown on screen (d, L, |V|, norms, coordinates, next-token
probabilities, completions) is computed here and saved to data/practical_example.json, which the
Manim scenes read. Setup follows the ActAdd post/code: "Love" − "Hate", layer 6, coefficient +5,
sampling temperature=1, top_p=0.3, freq_penalty=1 (github.com/montemac/activation_additions).
Completions are seeded and *not* cherry-picked: seed 0 is the one shown in the video.
"""

import json

import torch

from steering_explainer.config import Settings
from steering_explainer.log import get_logger
from steering_explainer.steering.intervene import next_token_probs, sample, steering
from steering_explainer.steering.model import encode, token_strings
from steering_explainer.steering.vectors import actadd_vector, pad_pair, resid_pre

log = get_logger(__name__)


def _top(tok, probs: torch.Tensor, k: int = 5) -> list[list]:
    """[[token string, probability], ...] for the k most likely next tokens."""
    p, i = probs.topk(k)
    return [[tok.decode([int(t)]), round(float(q), 4)] for q, t in zip(p, i)]


def _round(xs, nd=3) -> list[float]:
    return [round(float(x), nd) for x in xs]


def run_practical_example(s: Settings, model, tok) -> dict:
    """Compute every on-screen GPT-2-XL number and save data/practical_example.json."""
    dev, L, a = s.device, s.steer_layer, s.steer_coeff
    plus_ids, minus_ids = pad_pair(tok, s.prompt_plus, s.prompt_minus, dev)  # [<|endoftext|>, Love] vs [.., Hate]
    vec = actadd_vector(model, tok, s.prompt_plus, s.prompt_minus, L)  # h_A ∈ ℝ^{n×d}
    h_plus, h_minus = resid_pre(model, plus_ids, L), resid_pre(model, minus_ids, L)
    prompt_ids = encode(tok, s.example_prompt, dev)
    h_prompt = resid_pre(model, prompt_ids, L)  # h_ℓ at every prompt position (unsteered)
    cos = torch.nn.functional.cosine_similarity(h_plus[1], h_minus[1], dim=0)  # how similar Love and Hate look

    p_base = next_token_probs(model, prompt_ids)[0]  # softmax(W_U h_L) at "because"
    with steering(model, L, vec, alphas=a):
        p_steer = next_token_probs(model, prompt_ids)[0]
    delta = p_steer - p_base  # which next tokens gained / lost probability

    completions = []
    for seed in s.seeds:  # same seed for both rows -> paired comparison
        g = torch.Generator(device=dev).manual_seed(seed)
        batch = prompt_ids.repeat(2, 1)  # row 0 unsteered (α=0), row 1 steered (α=+5)
        with steering(model, L, vec, alphas=torch.tensor([0.0, a])):
            out = sample(model, batch, s.max_new_tokens, s.temperature, s.top_p, s.freq_penalty, g)
        texts = [tok.decode(o[prompt_ids.shape[1]:]) for o in out]  # completion only
        completions.append({"seed": seed, "unsteered": texts[0], "steered": texts[1]})
        log.info("PROMPT: %r | seed %d\n  UNSTEERED: %r\n  STEERED (alpha=%+g): %r", s.example_prompt, seed, texts[0], a, texts[1])

    cfg = model.config
    result = {
        "model": {"name": s.model_name, "n_layers": cfg.n_layer, "d_model": cfg.n_embd, "d_vocab": cfg.vocab_size,
                  "n_params": sum(p.numel() for p in model.parameters()), "dtype": s.dtype},
        "layer": L, "coeff": a, "prompt_plus": s.prompt_plus, "prompt_minus": s.prompt_minus,
        "tokens_plus": token_strings(tok, plus_ids), "tokens_minus": token_strings(tok, minus_ids),
        "prompt": s.example_prompt, "tokens_prompt": token_strings(tok, prompt_ids),
        "token_ids_prompt": prompt_ids[0].tolist(),
        "h_plus_first6": _round(h_plus[1, :6]), "h_minus_first6": _round(h_minus[1, :6]),
        "h_A_first6": _round(vec[1, :6]), "h_A_norm_per_pos": _round(vec.norm(dim=-1)),
        "h_plus_norm": round(float(h_plus[1].norm()), 2), "h_minus_norm": round(float(h_minus[1].norm()), 2),
        "cos_plus_minus": round(float(cos), 4),
        "h_prompt_norm_per_pos": _round(h_prompt.norm(dim=-1), 2),
        "relative_norm_pos1": round(float(vec[1].norm() / h_prompt[1].norm()), 3),  # ActAdd App. F RelativeNorm
        "next_token": {"unsteered_top5": _top(tok, p_base), "steered_top5": _top(tok, p_steer),
                       "largest_gains": _top(tok, delta), "largest_losses": [[t, -q] for t, q in _top(tok, -delta)]},
        "sampling": {"temperature": s.temperature, "top_p": s.top_p, "freq_penalty": s.freq_penalty,
                     "max_new_tokens": s.max_new_tokens},
        "completions": completions,
    }
    path = s.data_dir / "practical_example.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Practical example saved to %s:\n%s", path, json.dumps(result, indent=2, ensure_ascii=False))
    return result
