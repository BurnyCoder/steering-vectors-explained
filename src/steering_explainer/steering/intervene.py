"""intervene.py — add α·v to the residual stream during the forward pass, and sample text.

Global context: the steering intervention h̃_ℓ^(t) = h_ℓ^(t) + α·v_ℓ^(t) for the front positions
t < n (ActAdd's "front" alignment a = 1). It is implemented as a PyTorch forward *pre*-hook on
block ℓ, i.e. it edits the block's input before attention runs ("before attention layer 6").
Position safety: the hook reads the absolute `position_ids` that GPT2Model passes to every block
(transformers/models/gpt2/modeling_gpt2.py), so with a KV cache the later one-token steps
(positions ≥ n) are correctly left alone — tests/test_steering.py::test_kv_cache_matches_no_cache.
`sample` mirrors TransformerLens' sampler used by ActAdd: logits/temperature, minus
freq_penalty·(token counts so far), then nucleus (top-p) filtering, then a multinomial draw.
"""

from contextlib import contextmanager

import torch

from steering_explainer.steering.model import blocks


def _make_hook(vec: torch.Tensor, alphas):
    """Build a pre-hook adding alphas[b]·vec[b, t] to batch row b at absolute positions t < n."""
    vec = vec if vec.dim() == 3 else vec.unsqueeze(0)  # [n,d] -> [1,n,d] (broadcast over batch)
    n = vec.shape[1]  # number of steered front positions

    def hook(module, args, kwargs):
        h = args[0] if args else kwargs["hidden_states"]  # [B, seq, d] residual stream entering block ℓ
        pos = kwargs["position_ids"].reshape(-1)[-h.shape[1]:]  # absolute positions of this chunk
        sel = pos < n  # which positions of this chunk are front positions
        if not bool(sel.any()):  # cached one-token steps beyond the front: nothing to add
            return None  # returning None keeps the original inputs
        a = torch.as_tensor(alphas, dtype=torch.float32, device=h.device).reshape(-1, 1, 1)  # [B or 1,1,1]
        add = (a * vec[:, pos[sel]].to(h.device)).to(h.dtype)  # α·v at the selected positions
        h = h.clone()  # don't mutate a tensor autograd/other hooks may share
        h[:, sel] = h[:, sel] + add  # h̃ = h + α·v
        return ((h,) + tuple(args[1:]), kwargs) if args else (args, {**kwargs, "hidden_states": h})

    return hook


@contextmanager
def steering(model, layer: int, vec: torch.Tensor, alphas=1.0):
    """Context manager: while active, block `layer` receives h + α·v (α may differ per batch row)."""
    handle = blocks(model)[layer].register_forward_pre_hook(_make_hook(vec, alphas), with_kwargs=True)
    try:
        yield
    finally:
        handle.remove()


def _top_p_filter(logits: torch.Tensor, top_p: float) -> torch.Tensor:
    """Nucleus filtering as in TransformerLens utils.sample_logits / HF TopPLogitsWarper."""
    sorted_logits, idx = torch.sort(logits, descending=True)
    cum = sorted_logits.softmax(dim=-1).cumsum(dim=-1)  # cumulative probability mass
    remove = cum > top_p  # tokens beyond the nucleus
    remove[..., 1:] = remove[..., :-1].clone()  # shift right: keep the token that crosses top_p
    remove[..., 0] = False  # always keep the most likely token
    mask = remove.scatter(-1, idx, remove)  # back to vocabulary order
    return logits.masked_fill(mask, float("-inf"))


@torch.no_grad()
def sample(model, ids: torch.Tensor, max_new_tokens: int, temperature: float = 1.0, top_p: float = 1.0,
           freq_penalty: float = 0.0, generator: torch.Generator | None = None, use_cache: bool = True) -> torch.Tensor:
    """Autoregressively extend `ids` [B, n] by `max_new_tokens`; temperature 0 = greedy."""
    seq, past, inp = ids, None, ids  # full sequence, KV cache, tokens fed this step
    vocab = model.config.vocab_size
    for _ in range(max_new_tokens):
        out = model(input_ids=inp, past_key_values=past, use_cache=use_cache)
        logits = out.logits[:, -1].float()  # next-token scores z ∈ ℝ^{|V|} per row
        if temperature == 0:
            nxt = logits.argmax(dim=-1, keepdim=True)  # greedy decoding
        else:
            logits = logits / temperature
            if freq_penalty:  # subtract penalty × how often each token already occurs (TransformerLens semantics)
                counts = torch.zeros(seq.shape[0], vocab, device=seq.device).scatter_add_(
                    1, seq, torch.ones_like(seq, dtype=torch.float32))
                logits = logits - freq_penalty * counts
            probs = _top_p_filter(logits, top_p).softmax(dim=-1)  # p = softmax(filtered logits)
            nxt = torch.multinomial(probs, 1, generator=generator)  # one sampled token per row
        seq = torch.cat([seq, nxt], dim=1)
        past, inp = (out.past_key_values, nxt) if use_cache else (None, seq)  # cache: feed only the new token
    return seq


@torch.no_grad()
def next_token_probs(model, ids: torch.Tensor) -> torch.Tensor:
    """softmax(W_U h_L) at the last position: the model's next-token distribution, [B, |V|]."""
    return model(ids).logits[:, -1].float().softmax(dim=-1)


@torch.no_grad()
def completion_nll(model, ids: torch.Tensor, prompt_len: int) -> torch.Tensor:
    """Mean negative log-likelihood (nats/token) of tokens after `prompt_len`, per row: fluency metric."""
    logp = model(ids).logits[:, :-1].float().log_softmax(dim=-1)  # predictions for tokens 1..T
    tgt = ids[:, 1:]  # the tokens actually present
    tok_lp = logp.gather(-1, tgt.unsqueeze(-1)).squeeze(-1)  # log p(token_t | tokens_<t)
    return -tok_lp[:, prompt_len - 1:].mean(dim=-1)  # average over completion tokens only
