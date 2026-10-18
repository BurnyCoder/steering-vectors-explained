"""model.py — load a GPT-2 checkpoint with Hugging Face transformers and tokenize like ActAdd.

Global context: ActAdd's original code (TransformerLens) prepends the <|endoftext|> token to every
prompt; the LessWrong post states it is "automatically prepended by the tokenizer". HF's GPT-2
tokenizer does not add it, so `encode` does it explicitly — this is why ActAdd's position-0
difference is exactly zero. TransformerLens 4 removed HookedTransformer, so we use plain HF +
PyTorch hooks (docs: https://huggingface.co/docs/transformers/model_doc/gpt2).
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from steering_explainer.log import get_logger

log = get_logger(__name__)


def load_model(name: str, device: str, dtype: str):
    """Return (model, tokenizer) in eval mode; `dtype` is a torch dtype name such as "float16"."""
    tok = AutoTokenizer.from_pretrained(name)  # byte-level BPE, |V| = 50257 for GPT-2
    model = AutoModelForCausalLM.from_pretrained(name, dtype=getattr(torch, dtype))  # weights in chosen precision
    model.to(device).eval()  # eval(): disables dropout so forward passes are deterministic
    cfg = model.config  # n_layer, n_embd (= d), vocab_size
    log.info("Loaded %s on %s (%s): L=%d layers, d=%d, |V|=%d, params=%.3fB", name, device, dtype,
             cfg.n_layer, cfg.n_embd, cfg.vocab_size, sum(p.numel() for p in model.parameters()) / 1e9)
    return model, tok


def encode(tok, text: str, device: str) -> torch.Tensor:
    """Token ids [1, n] with <|endoftext|> (GPT-2's BOS) prepended, as TransformerLens/ActAdd do."""
    ids = [tok.bos_token_id] + tok.encode(text)  # bos_token_id == 50256 == <|endoftext|>
    return torch.tensor([ids], device=device)


def blocks(model):
    """The list of transformer blocks (GPT-2: model.transformer.h); block ℓ's input is h_ℓ."""
    return model.transformer.h


def token_strings(tok, ids: torch.Tensor) -> list[str]:
    """Human-readable token strings for a [1, n] id tensor (used on screen)."""
    return [tok.decode([i]) for i in ids[0].tolist()]
