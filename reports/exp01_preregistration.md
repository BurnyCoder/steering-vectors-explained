# Experiment 01 — Pre-registration: dose-response of the "Love" − "Hate" steering vector on GPT-2-XL

*Written and committed before any pilot or study data were generated. Author: Libor Burian (independent researcher).*

## Question
Does adding the ActAdd steering vector h_A = h_ℓ("Love") − h_ℓ("Hate") to GPT-2-XL's residual
stream (input of block ℓ = 6, front positions, <|endoftext|> prepended) make continuations of
*unrelated* text more positive, and is the effect specific to that direction rather than to perturbing
the residual stream by the same amount?

## Hypotheses
* **H1 (primary, directional specificity):** at α = 5, completions steered with h_A are more positive than
  completions steered with random directions of identical per-position norm.
* **H2 (dose-response):** positivity increases monotonically with α over α ∈ [-5.0, 0.0, 2.0, 5.0, 10.0, 15.0].
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
* Model: `gpt2-xl` (float16), Hugging Face transformers; steering by a forward pre-hook on block 6.
* Steering vector: ActAdd (Turner et al. 2024): prompts "Love" / "Hate", right-padded with ' ' if lengths differ.
* Prompts: IMDb test split (Maas et al. 2011), shuffled with seed 0, alternating negative/positive labels, first
  8 words of each review (`<br />` removed). The first 20 prompts form the pilot; the main study
  uses the *next* N prompts (disjoint from the pilot).
* Conditions per prompt and seed (one batch): steered α ∈ [-5.0, 0.0, 2.0, 5.0, 10.0, 15.0]; random controls at α ∈ [5.0, 15.0]
  with R = 5 fixed random directions (Gaussian, rescaled to ‖h_A‖ at every position; generated once with seed 1234).
* Sampling (official ActAdd settings): temperature 1.0, top-p 0.3, frequency penalty 1.0,
  40 new tokens, seeds [0, 1, 2] (one independent completion per seed).

## Metrics
* **Primary:** P(positive) of the completion text alone (prompt excluded), from `siebert/sentiment-roberta-large-english`
  (SiEBERT, Hartmann et al. 2023), an external classifier not used to build the vector.
* **Secondary:** mean per-token NLL (nats) of the completion under the *unsteered* model (fluency cost).

## Sample size
Pilot (n = 20): estimate d_z of the primary difference; N = required n for 80% power at two-sided α = 0.05 (paired
t-test approximation, statsmodels TTestPower), clipped to [30, 200]. Pilot prompts are never reused.

## Analysis plan
* Unit of analysis = prompt. Per prompt: average over seeds (and over the R random directions).
* Primary: mean difference with 95% percentile bootstrap CI (10000 resamples, seed 0).
* Secondary: Wilcoxon signed-rank tests of steer(α) − steer(0) for every α ≠ 0 and of steer(15) − random(15),
  Holm-corrected as one family; per-prompt Spearman ρ(α, P_pos) with bootstrap CI; NLL differences with CIs.
* Robustness: the primary difference recomputed for each seed separately.
* Exclusions: none. An empty completion is scored as the neutral string "." (the classifier needs non-empty input).
* Anything not listed here is reported as **post-hoc**.
