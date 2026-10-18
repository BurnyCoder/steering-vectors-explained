# All experiments — what was run, what was found, what was learned

*Author: Libor Burian (independent researcher). Plain-language overview and glossary: [summary.md](summary.md).
Numbers: [results_tables.md](results_tables.md). Paper: [paper/paper.pdf](paper/paper.pdf).*

## Overview
| # | Question | N (prompts) | Pre-registration | Primary result |
|---|---|---|---|---|
| Practical example | Reproduce ActAdd "Love" − "Hate" on "I hate you because" | 1 prompt, 3 seeds | — (descriptive) | `data/practical_example.json`: seed-0 steered text turns to love |
| 01 | Is the vector better than a random push of equal norm? | 30 (+20 pilot) | [exp01](exp01_preregistration.md) | **supported**: +0.125 [+0.045, +0.203] |
| 02 | Is steering better than not steering? | 190 | [exp02](exp02_preregistration.md) | **supported**: +0.146 [+0.102, +0.192] |
| post-hoc | Why did α = −5 not lower positivity? | exp01 + exp02 | none (exploratory) | the vector injects the words: "hate" (whole word) in 22.5% at α = −5, rated as positive as unsteered text |

Details: [exp01_love_hate_dose_response.md](exp01_love_hate_dose_response.md),
[exp02_powered_replication.md](exp02_powered_replication.md).

## Choices and why
* **GPT-2-XL, layer 6, coefficient +5, "Love" − "Hate".**
  * This is exactly the ActAdd demo: the LessWrong post says "Love" − "Hate" before attention layer 6 with
    coefficient +5, and the repo README sets `coeff=5, act_name="blocks.6.hook_resid_pre"`.
  * The video's practical example is therefore a faithful reproduction, not a new setting.
  * GPT-2-XL fits in 8 GB in float16.
* **Sampling: temperature 1, top-p 0.3, frequency penalty 1.** These are the official ActAdd settings
  (`scripts/basic_functionality.py`). Our sampler re-implements TransformerLens' order of operations:
  temperature, then frequency penalty over all tokens so far, then top-p.
* **α grid {−5, 0, 2, 5, 10, 15}.** It covers:
  * the sign flip (−5);
  * small, ActAdd's value, and large values;
  * up to the edge of ActAdd's "typical … magnitude less than 15" (§3, footnote 2).
* **Random controls: R = 5 Gaussian directions, rescaled to ‖h_A‖ position by position.** This separates
  "this direction" from "any perturbation of this size".
* **IMDb review prefixes (8 words).** They are text unrelated to the contrast prompts, with balanced
  sentiment, so the vector is never built from evaluation data.
* **SiEBERT.** It is a robust binary sentiment model, trained on 15 datasets and independent of GPT-2.
* **40 new tokens and 3 seeds.** This fits the compute budget: about 3 s per batch of 16 conditions on an
  RTX 5070 Laptop GPU.
* **Statistics: paired design, bootstrap CIs, Wilcoxon + Holm, pilot-based power.** These follow Lones (2021)
  and the NeurIPS checklist: error bars, a pre-specified analysis, multiple-comparison control.

## Issues met, causes, fixes (chronological)
1. **TransformerLens 4 removed `HookedTransformer`.**
   * Cause: the ImportError message pointed to the v4 migration guide.
   * Fix: plain Hugging Face `transformers` with a PyTorch forward *pre*-hook on `model.transformer.h[ℓ]`.
     That is the same tensor as TransformerLens' `blocks.ℓ.hook_resid_pre`, with fewer dependencies.
2. **Front-position hooks and the KV cache.**
   * Risk: a naive hook adds the vector to *every* new token, because a cached step has sequence length 1
     and local position 0.
   * Fix: the hook reads the absolute `position_ids` that `GPT2Model` passes to each block.
   * Test: cached and uncached greedy generations are identical.
3. **The Hugging Face GPT-2 tokenizer does not prepend `<|endoftext|>`; TransformerLens does.**
   * Fix: prepend it explicitly. The measured position-0 difference is then exactly 0, as ActAdd's
     Appendix F states.
4. **"Hate" is two tokens ("H", "ate").**
   * Fix: right-pad "Love" with the space token, per ActAdd Algorithm 1 and Appendix C.
   * Caveat: the 2023 README demo used no padding (`pad_method=None`), which subtracts the raw "ate"
     activation at position 2. We follow the paper and document the difference.
5. **Experiment 01's power covered only its primary contrast.**
   * Steered vs. unsteered had d_z = 0.205, so N = 30 was underpowered.
   * Fix: experiment 02, pre-registered with N = 190 computed from that effect size.
6. **α = −5 did not lower positivity.** A post-hoc reading showed lexical injection of "hate", quantified
   in `study/posthoc.py` and labelled exploratory.
7. **Engineering for the video:**
   * Pillow 13 broke Manim's `ImageMobject`; pinned `pillow<12`.
   * Windows cp1252 consoles crashed the log on "ℓ"; set UTF-8.
   * Parallel renders shared manim-voiceover's `cache.json`; now one cache per chapter.
   * Contact-sheet QA found clipped and overlapping text in chapters 0, 2-5 and 7-11; each was fixed and
     re-checked.
8. **Independent fact-check of the v1.0 video** ([docs/fact_check.md](../docs/fact_check.md)): 25 errors, fixed in v1.1.
   * The post-hoc substring patterns overcounted ("whatever" contains "hate"); whole-word counts lower "hate" at
     α = −5 from 29.5% to 22.5%.
   * The narration said "same random choices", but batched sampling only shares the seed. It said GPT-2 itself
     prepends `<|endoftext|>`, but that is TransformerLens' default (item 3 above).
   * The narration said ActAdd is exactly the |D| = 1 case of CAA, which is not so: ActAdd has no completions and
     keeps one difference per position.
   * The pre-registered H2 was never spoken; every pre-registered hypothesis is now voiced.

## Overall conclusions (with confidence)
* **High confidence** (pre-registered, replicated, per-seed robust): on GPT-2-XL, adding the ActAdd
  "Love" − "Hate" vector at layer 6 with α = 5 raises the SiEBERT-positivity of continuations of movie-review
  openings by about 0.13-0.15 (absolute probability), relative to both no steering and equal-norm random
  directions.
* **High confidence:** steering costs fluency, and more so than random pushes of equal norm at α ≥ 10.
* **Moderate confidence** (one experiment each way): the effect is non-monotone. Mean positivity is highest at
  α = 10 (the 10 vs 5 difference was not tested) and drops at 15 as text degrades.
* **Exploratory:**
  * The vector acts substantially through word identity: "love"/"hate" appear far more often.
  * The negative direction is not "negative sentiment".
  * Sentiment and lexical effects are not separated here.

## Limits of these experiments
* One model, one layer, one vector, one dataset, one classifier.
* Binary classifier with no neutral class: baseline positivity was already 0.67-0.75.
* 40-token continuations.
* Isotropic random directions are a weaker control than an unrelated *real* steering vector of equal norm.
