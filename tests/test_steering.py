"""test_steering.py — correctness of the activation-addition machinery on GPT-2 small.

Global context: the study and the video's "practical example" run GPT-2-XL; these tests use the
same code on the 124M `gpt2` checkpoint (identical architecture family, fast to download) to check
the properties every steering claim depends on:
  1. α = 0 changes nothing;           2. the hook adds exactly α·v at the front positions only;
  3. KV-cached generation == uncached generation (the hook must not re-fire on cached steps);
  4. ActAdd's position-0 difference is 0 (both prompts start with <|endoftext|>);
  5. right-padding with ' ' equalises lengths;  6. random controls match per-position norms.
"""

import pytest
import torch

from steering_explainer.steering import intervene, model as mdl, vectors

pytestmark = pytest.mark.gpu  # needs model weights; skip with -m "not gpu"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


@pytest.fixture(scope="module")
def gpt2():
    return mdl.load_model("gpt2", DEVICE, "float32")  # (model, tokenizer)


def test_alpha_zero_is_identity(gpt2):
    m, tok = gpt2
    ids = mdl.encode(tok, "I hate you because", DEVICE)
    vec = vectors.actadd_vector(m, tok, "Love", "Hate", layer=6)
    base = m(ids).logits
    with intervene.steering(m, 6, vec, alphas=0.0):
        steered = m(ids).logits
    assert torch.equal(base, steered)


def test_hook_adds_exactly_alpha_v_at_front_positions(gpt2):
    m, tok = gpt2
    ids = mdl.encode(tok, "I hate you because", DEVICE)
    vec = vectors.actadd_vector(m, tok, "Love", "Hate", layer=6)  # shape [n, d]
    clean = vectors.resid_pre(m, ids, 6)  # [seq, d]
    with intervene.steering(m, 6, vec, alphas=5.0):
        steered = vectors.resid_pre(m, ids, 6)  # capture hook registered after the steering hook
    delta = steered - clean
    n = vec.shape[0]
    assert torch.allclose(delta[:n], 5.0 * vec, atol=1e-4)  # exactly α·v at positions 0..n-1
    assert torch.count_nonzero(delta[n:]) == 0  # untouched elsewhere


def test_kv_cache_matches_no_cache(gpt2):
    m, tok = gpt2
    ids = mdl.encode(tok, "I hate you because", DEVICE)
    vec = vectors.actadd_vector(m, tok, "Love", "Hate", layer=6)
    with intervene.steering(m, 6, vec, alphas=5.0):
        cached = intervene.sample(m, ids, 12, temperature=0.0, use_cache=True)
        uncached = intervene.sample(m, ids, 12, temperature=0.0, use_cache=False)
    assert torch.equal(cached, uncached)


def test_actadd_position_zero_difference_is_zero(gpt2):
    m, tok = gpt2
    vec = vectors.actadd_vector(m, tok, "Love", "Hate", layer=6)
    assert torch.count_nonzero(vec[0]) == 0  # <|endoftext|> vs <|endoftext|>
    assert vec[1].norm() > 0


def test_right_padding_with_space_token(gpt2):
    _, tok = gpt2
    a, b = vectors.pad_pair(tok, "I talk about weddings constantly", "I do not talk about weddings constantly", DEVICE)
    assert a.shape == b.shape
    assert a[0, -1].item() == tok.encode(" ")[0]  # the shorter prompt was right-padded with ' '


def test_random_control_matches_per_position_norm(gpt2):
    m, tok = gpt2
    vec = vectors.actadd_vector(m, tok, "Love", "Hate", layer=6)
    g = torch.Generator(device="cpu").manual_seed(0)
    rnd = vectors.random_like(vec, g)
    assert torch.allclose(rnd.norm(dim=-1), vec.norm(dim=-1), rtol=1e-4)
    assert torch.nn.functional.cosine_similarity(rnd[1], vec[1], dim=0).abs() < 0.2  # a different direction


def test_mean_difference_formula():
    plus = torch.tensor([[3.1, 1.3], [2.8, 0.5], [2.6, 2.2]])
    minus = torch.tensor([[1.0, 1.0], [1.0, 1.0], [0.5, 2.0]])
    assert torch.allclose(vectors.mean_difference(plus, minus), torch.tensor([2.0, 0.0]), atol=1e-6)


def test_per_row_alphas_in_one_batch(gpt2):
    m, tok = gpt2
    ids = mdl.encode(tok, "I hate you because", DEVICE).repeat(2, 1)  # same prompt twice
    vec = vectors.actadd_vector(m, tok, "Love", "Hate", layer=6)
    with intervene.steering(m, 6, vec, alphas=torch.tensor([0.0, 5.0])):
        batched = m(ids).logits
    single = m(ids[:1]).logits
    assert torch.allclose(batched[0], single[0], atol=1e-4)  # row with α=0 equals unsteered
    assert not torch.allclose(batched[1], single[0], atol=1e-2)  # row with α=5 differs
