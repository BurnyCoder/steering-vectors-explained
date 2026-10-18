"""vectors.py — read residual-stream activations and build steering / control vectors.

Global context:
* `resid_pre` reads h_ℓ, the residual stream *entering* block ℓ (TransformerLens name
  `blocks.ℓ.hook_resid_pre`; ActAdd: "the residual stream values h^l input to layer l").
* `actadd_vector` = ActAdd Algorithm 1: h_A = h_ℓ(p⁺) − h_ℓ(p⁻), one row per token position,
  after right-padding the shorter prompt with ' ' tokens (ActAdd Appendix C; README pad_method="tokens_right").
* `mean_difference` = CAA Eq. 1: v = (1/|D|) Σ [a(p,c⁺) − a(p,c⁻)] (Rimsky et al. 2024).
* `random_like` = control: random Gaussian directions with the same per-position norms.
"""

import torch

from steering_explainer.steering.model import blocks, encode


@torch.no_grad()
def resid_pre(model, ids: torch.Tensor, layer: int) -> torch.Tensor:
    """Return h_layer for the first sequence of `ids` as a [seq, d] float32 tensor."""
    captured = {}

    def grab(module, args, kwargs):  # forward pre-hook: sees the block's input before it runs
        captured["h"] = (args[0] if args else kwargs["hidden_states"]).detach()

    handle = blocks(model)[layer].register_forward_pre_hook(grab, with_kwargs=True)  # PyTorch hook API
    try:
        model(ids)  # one forward pass fills `captured`
    finally:
        handle.remove()  # never leave hooks behind
    return captured["h"][0].float()  # first batch row, float32 for exact arithmetic downstream


def pad_pair(tok, plus: str, minus: str, device: str) -> tuple[torch.Tensor, torch.Tensor]:
    """Encode both prompts and right-pad the shorter one with the ' ' token to equal length."""
    a, b = encode(tok, plus, device), encode(tok, minus, device)
    space = tok.encode(" ")[0]  # GPT-2 id of a single space token
    n = max(a.shape[1], b.shape[1])
    pad = lambda x: torch.cat([x, torch.full((1, n - x.shape[1]), space, device=device)], dim=1)
    return pad(a), pad(b)


def actadd_vector(model, tok, plus: str, minus: str, layer: int) -> torch.Tensor:
    """ActAdd steering 'vector' h_A ∈ ℝ^{n×d}: one difference vector per front position."""
    device = next(model.parameters()).device  # same device as the weights
    a, b = pad_pair(tok, plus, minus, device)
    return resid_pre(model, a, layer) - resid_pre(model, b, layer)  # h_ℓ(p⁺) − h_ℓ(p⁻)


def mean_difference(acts_plus: torch.Tensor, acts_minus: torch.Tensor) -> torch.Tensor:
    """CAA mean difference over |D| rows: (1/|D|) Σ_i [plus_i − minus_i] -> [d]."""
    return (acts_plus - acts_minus).mean(dim=0)  # mean over the dataset axis


def random_like(vec: torch.Tensor, generator: torch.Generator) -> torch.Tensor:
    """Random directions with the same norm as each row of `vec` (zero rows stay zero)."""
    g = torch.randn(vec.shape, generator=generator).to(vec.device)  # isotropic Gaussian on CPU RNG
    g = g / g.norm(dim=-1, keepdim=True)  # unit vectors: uniformly random directions
    return g * vec.norm(dim=-1, keepdim=True)  # rescale to match ‖h_A‖ position by position
