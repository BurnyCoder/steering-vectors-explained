"""design.py — the pre-registered hypothesis, metrics, conditions and analysis plan.

Global context: `write_preregistration` renders this design (from .env settings) to
reports/exp01_preregistration.md, which is committed to git *before* the pilot or study runs, so
the analysis cannot be tuned to the data (pre-registration practice: Nosek et al. 2018, PNAS,
https://doi.org/10.1073/pnas.1708274114; NeurIPS checklist on pre-specifying analyses).
"""

from dataclasses import dataclass

from steering_explainer.config import Settings

PRIMARY_ALPHA = 5.0  # ActAdd's coefficient for "Love" − "Hate" (LessWrong post; repo README)


@dataclass(frozen=True)
class Condition:
    """One row of a generation batch: steer with the real vector or a random control at coefficient α."""
    kind: str  # "steer" or "random"
    alpha: float
    rand_idx: int = -1  # which random direction (random rows only)

    @property
    def name(self) -> str:
        return f"steer_{self.alpha:g}" if self.kind == "steer" else f"random{self.rand_idx}_{self.alpha:g}"


def conditions(s: Settings) -> list[Condition]:
    """All conditions in a fixed order: steered grid first, then R random directions per control α."""
    steer = [Condition("steer", a) for a in s.alphas]
    rand = [Condition("random", a, r) for a in s.random_alphas for r in range(s.n_random)]
    return steer + rand


def preregistration_markdown(s: Settings) -> str:
    """The pre-registration document (all numbers come from Settings)."""
    return f"""# Experiment 01 — Pre-registration: dose-response of the "Love" − "Hate" steering vector on GPT-2-XL

*Written and committed before any pilot or study data were generated. Author: Libor Burian (independent researcher).*

## Question
Does adding the ActAdd steering vector h_A = h_ℓ("{s.prompt_plus}") − h_ℓ("{s.prompt_minus}") to GPT-2-XL's residual
stream (input of block ℓ = {s.steer_layer}, front positions, <|endoftext|> prepended) make continuations of
*unrelated* text more positive, and is the effect specific to that direction rather than to perturbing
the residual stream by the same amount?

## Hypotheses
* **H1 (primary, directional specificity):** at α = {PRIMARY_ALPHA:g}, completions steered with h_A are more positive than
  completions steered with random directions of identical per-position norm.
* **H2 (dose-response):** positivity increases monotonically with α over α ∈ {list(s.alphas)}.
* **H3 (sign):** α = −5 makes completions less positive than α = 0.
* **H4 (cost):** steering increases completion negative log-likelihood (NLL) under the unsteered model,
  more at larger |α|.

## Falsification criteria (decided in advance)
* H1 is **falsified** if the 95% paired-bootstrap CI of mean[P_pos(steer, α=5) − P_pos(random, α=5)]
  includes 0 or lies below 0.
* H2 is falsified if the 95% bootstrap CI of the mean per-prompt Spearman ρ(α, P_pos) includes 0 or is negative.
* H3 is falsified if the Holm-adjusted Wilcoxon p ≥ 0.05 or the mean difference has the wrong sign.
* H4 is falsified if the 95% bootstrap CI of NLL(steer, α=15) − NLL(steer, α=0) includes 0 or lies below 0.

## Model, data, conditions
* Model: `{s.model_name}` ({s.dtype}), Hugging Face transformers; steering by a forward pre-hook on block {s.steer_layer}.
* Steering vector: ActAdd (Turner et al. 2024): prompts "{s.prompt_plus}" / "{s.prompt_minus}", right-padded with ' ' if lengths differ.
* Prompts: IMDb test split (Maas et al. 2011), shuffled with seed 0, alternating negative/positive labels, first
  {s.prompt_words} words of each review (`<br />` removed). The first {s.n_pilot} prompts form the pilot; the main study
  uses the *next* N prompts (disjoint from the pilot).
* Conditions per prompt and seed (one batch): steered α ∈ {list(s.alphas)}; random controls at α ∈ {list(s.random_alphas)}
  with R = {s.n_random} fixed random directions (Gaussian, rescaled to ‖h_A‖ at every position; generated once with seed 1234).
* Sampling (official ActAdd settings): temperature {s.temperature}, top-p {s.top_p}, frequency penalty {s.freq_penalty},
  {s.max_new_tokens} new tokens, seeds {list(s.seeds)} (one independent completion per seed).

## Metrics
* **Primary:** P(positive) of the completion text alone (prompt excluded), from `{s.sentiment_model}`
  (SiEBERT, Hartmann et al. 2023), an external classifier not used to build the vector.
* **Secondary:** mean per-token NLL (nats) of the completion under the *unsteered* model (fluency cost).

## Sample size
Pilot (n = {s.n_pilot}): estimate d_z of the primary difference; N = required n for 80% power at two-sided α = 0.05 (paired
t-test approximation, statsmodels TTestPower), clipped to [{s.n_min}, {s.n_max}]. Pilot prompts are never reused.

## Analysis plan
* Unit of analysis = prompt. Per prompt: average over seeds (and over the R random directions).
* Primary: mean difference with 95% percentile bootstrap CI ({s.bootstrap_resamples} resamples, seed 0).
* Secondary: Wilcoxon signed-rank tests of steer(α) − steer(0) for every α ≠ 0 and of steer(15) − random(15),
  Holm-corrected as one family; per-prompt Spearman ρ(α, P_pos) with bootstrap CI; NLL differences with CIs.
* Robustness: the primary difference recomputed for each seed separately.
* Exclusions: none. An empty completion is scored as the neutral string "." (the classifier needs non-empty input).
* Anything not listed here is reported as **post-hoc**.
"""


def write_preregistration(s: Settings) -> None:
    path = s.reports_dir / "exp01_preregistration.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(preregistration_markdown(s), encoding="utf-8")
