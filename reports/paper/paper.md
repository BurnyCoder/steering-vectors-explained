---
title: "Steering Vectors from Scratch: a Source-Verified Explainer and a Pre-registered Dose–Response Test of Activation Addition on GPT-2-XL"
author: "Libor Burian, independent researcher"
date: "October 2026"
abstract: |
  Steering vectors change a language model's behaviour by adding a fixed vector to its residual-stream activations at inference time. We contribute two things. (i) A narrated 12-chapter animated explainer that defines every symbol of the two central equations (the mean-difference vector of Contrastive Activation Addition and the additive intervention) before using it. The explainer is built with three mechanical guarantees: all 26 on-screen quotations are verified verbatim against their downloaded sources, every spoken or displayed number is computed by code, and a test fails if narration uses a term before the chapter that defines it. (ii) Two pre-registered experiments on the "Love" − "Hate" Activation Addition (ActAdd) vector of Turner et al. on GPT-2-XL (layer 6), with 8-word IMDb review openings, a norm-matched random-direction control and an independent sentiment classifier. Experiment 1 (N = 30 prompts) supports direction specificity: at coefficient α = 5, P(positive) exceeds equal-norm random directions by +0.125 (95% CI [0.045, 0.203]), but the gain over no steering is not significant. Experiment 2 is powered for that contrast (N = 190 new prompts) and finds +0.146 [0.102, 0.192] over no steering. It replicates direction specificity (+0.132 [0.097, 0.166]), shows a non-monotone dose–response peaking at α = 10, and a fluency cost of +1.38 nats/token at α = 15. The negated vector does not reduce positivity. A post-hoc analysis shows the vector largely injects the words themselves: "love" appears in 62.5% of α = 5 continuations and "hate" in 29.5% at α = −5.
---

# Introduction

Activation engineering modifies a model's activations at inference time to control its outputs. In the words of Turner et al.: "we introduce activation engineering: the inference-time modification of activations in order to control (or steer) model outputs" (Turner et al., 2024). Its simplest instance adds a *steering vector* to the residual stream. The vector is built either from one contrast pair (ActAdd, (Turner et al., 2024)) or as a mean difference over a dataset of contrastive completions (CAA, (Rimsky et al., 2024)). Related work steers attention heads (Li et al., 2023), reads and controls representation directions (Zou et al., 2023), ablates single directions (Arditi et al., 2024), or clamps sparse-autoencoder features (Templeton et al., 2024).

Two gaps motivate this work.

* **Teaching.** Introductions usually assume linear algebra and transformer internals. We build the full object from scalars upward, with no undefined symbol, and ground every quotation and number mechanically.
* **Evidence.** Canonical demonstrations are selected. The ActAdd blog post states "We slightly (best-of-3) cherry-picked our results" (Turner et al., 2023). Tan et al. report that "In-distribution, steerability is highly variable across different inputs" (Tan et al., 2024). We therefore test the canonical demo under pre-registration, with controls and confidence intervals.

# Background and notation

GPT-2 (Radford et al., 2019) maps tokens to vectors $h_0^{(t)}\in\mathbb{R}^d$ and updates them through $L$ blocks. Omitting LayerNorm, as in (Arditi et al., 2024):
$$h_{\ell+1}=h_\ell+\mathrm{Attn}_\ell(h_\ell)+\mathrm{MLP}_\ell\big(h_\ell+\mathrm{Attn}_\ell(h_\ell)\big),\qquad p=\mathrm{softmax}(W_U h_L).$$
The residual stream is "simply the sum of the output of all the previous layers and the original embedding" (Elhage et al., 2021). The linear representation hypothesis holds that "high-level concepts are represented linearly as directions in some representation space" (Park et al., 2024).

Given a dataset $\mathcal{D}$ of triples (prompt $p$, completion $c^+$ showing a behaviour, completion $c^-$ showing its opposite), CAA defines
$$v_\ell=\frac{1}{|\mathcal{D}|}\sum_{(p,c^+,c^-)\in\mathcal{D}}\Big[a_\ell(p,c^+)-a_\ell(p,c^-)\Big],\qquad \tilde h_\ell^{(t)}=h_\ell^{(t)}+\alpha\,v_\ell\quad(t\in T),$$
where $a_\ell(p,c)\in\mathbb{R}^d$ is the residual stream at layer $\ell$ and the completion's last token (Rimsky et al., 2024). ActAdd is the case $|\mathcal{D}|=1$ with prompts $p^\pm$. It produces one difference per token position, $h_A=h_\ell(p^+)-h_\ell(p^-)\in\mathbb{R}^{n\times d}$, added at the first $n$ positions of the user prompt (Turner et al., 2024).

# Method

## Explainer pipeline

* **Rendering and narration.** Twelve Manim scenes, narrated with Microsoft Edge neural TTS through manim-voiceover. Word-level timings from the TTS synchronise animations via bookmarks.
* **Mechanical guarantees:**
  * **Quotes.** All 26 quotations live in one registry and are checked as verbatim substrings, after whitespace and typography normalisation, of each source's downloaded HTML or PDF. Quotes from sources not licensed CC BY 4.0 are limited to 15 words.
  * **Numbers.** Toy numbers come from exact rational arithmetic, and real numbers from JSON files written by the experiment code. Unit tests pin both.
  * **Definition order.** A glossary maps 51 terms to their defining chapter, and a test fails if any earlier chapter's narration uses one.
* **Visual QA.** Contact sheets of rendered frames are inspected for overlaps and clipping.

## Steering implementation

* **Model:** GPT-2-XL (Radford et al., 2019): 48 layers, $d=1600$, $|V|=50{,}257$, 1.56 B parameters, float16.
* **Vector:** $h_A$ is read at the input of block 6, matching ActAdd's `blocks.6.hook_resid_pre`, from "<|endoftext|>Love" and "<|endoftext|>Hate". "Hate" tokenises as "H"+"ate", so "Love" is right-padded with a space (ActAdd Algorithm 1). The position-0 difference is exactly zero.
* **Intervention:** a forward pre-hook adds $\alpha h_A^{(t)}$ at absolute positions $t<3$. It is unit-tested for identity at $\alpha=0$, exact addition at the front positions only, and identical cached and uncached generation.
* **Sampling:** the official ActAdd settings (temperature 1, top-$p$ 0.3, frequency penalty 1) and 40 new tokens.

## Experiments

* **Prompts:** the first 8 words of IMDb test reviews (Maas et al., 2011), shuffled with seed 0, alternating labels.
* **Conditions:** for each prompt and each of 3 seeds, one batch contains the steered conditions $\alpha\in\{-5,0,2,5,10,15\}$ and $R=5$ random Gaussian directions rescaled to $\lVert h_A^{(t)}\rVert$ at $\alpha\in\{5,15\}$.
* **Primary metric:** SiEBERT P(positive) of the continuation alone (Hartmann et al., 2023).
* **Secondary metric:** continuation NLL under the unsteered model.
* **Analysis:** per-prompt averages; 10,000-resample percentile bootstrap CIs (Efron & Tibshirani, 1993); two-sided Wilcoxon tests, Holm-corrected (Holm, 1979); per-prompt Spearman $\rho$.
* **Experiment 1** was pre-registered (Nosek et al., 2018) with the primary contrast steer(5) − random(5). Its N came from a 20-prompt pilot ($d_z=0.633$, 80% power at N = 22, floor N = 30).
* **Experiment 2** was pre-registered after Experiment 1. Its primary contrast is steer(5) − steer(0), powered from Experiment 1's $d_z=0.205$ (N = 190 fresh prompts).

# Results

**Practical example.** For "I hate you because", the seed-0 unsteered continuation is hostile ("you're a stupid, boring person…"). The steered one reads "you're all the same. The world is full of people who are afraid to be themselves, and love is the only way to be true." The activations at position 1 have norms 98.0 ("Love") and 97.5 ("H") and cosine similarity 0.715. $\lVert h_A^{(1)}\rVert=73.8$, which is 0.82 of the prompt's own residual norm at that position.

Table 1: Pre-registered results (95% CI). Full tables: `reports/results_tables.md`.

| | Exp. 1 (N = 30) | Exp. 2 (N = 190) |
|---|---|---|
| steer(5) − random(5) | **+0.125 [+0.045, +0.203]** (primary) | +0.132 [+0.097, +0.166] |
| steer(5) − steer(0) | +0.056 [−0.042, +0.155] (Holm p = 0.22) | **+0.146 [+0.102, +0.192]** (primary) |
| mean per-prompt Spearman $\rho$ | +0.074 [−0.086, +0.225] | +0.164 [+0.101, +0.226] |
| steer(−5) − steer(0) | −0.025 [−0.153, +0.105] | +0.052 [−0.000, +0.105] |
| $\Delta$NLL at $\alpha=15$ (steer / random) | +1.42 / +0.84 | +1.38 / +0.74 |

![Experiment 2: P(positive) and NLL against $\alpha$. Points are means over 190 prompts × 3 seeds; bars are 95% bootstrap CIs; orange points are norm-matched random directions (offset horizontally for visibility).](figures/exp02_dose_response.png)

* **Experiment 2: every positive $\alpha$ beats no steering after Holm correction**:
  * $\alpha=2$: +0.101;
  * $\alpha=5$: +0.146;
  * $\alpha=10$: +0.168;
  * $\alpha=15$: +0.109.
* **The response peaks at $\alpha=10$** (mean 0.833) and declines at 15 (0.774).
* **Each seed alone** excludes zero for the primary contrast.

**Post-hoc (exploratory).** The share of continuations matching `lov` rises from 5.6% unsteered to 62.5% at $\alpha=5$. The share matching `hat(e|ing|red)` rises from 0.4% to 29.5% at $\alpha=-5$, typically in incoherent text that the classifier often rates positive.

# Discussion

**Claims, with evidence strength:**

* **Strong:** (i) the canonical ActAdd vector shifts GPT-2-XL continuations of unrelated text toward positive sentiment, by about 0.15 absolute probability at $\alpha=5$. (ii) The effect is specific to the direction, not to the size of the push. Both are pre-registered, and (ii) is replicated.
* **Supported:** the cost in fluency grows with $\alpha$ and exceeds that of random directions of the same norm at large $\alpha$.
* **Not supported:** monotone dose–response, and sign symmetry.

**Implications.**

* The negated vector is not an "anti-love" vector. Mechanically it adds the token identity of "H"/"ate".
* Much of the positive effect co-occurs with the literal word "love", consistent with ActAdd's framing of topic steering.
* Equal-norm random controls themselves change the metric (Experiment 1: −0.07 positivity). So "beats random" and "beats nothing" are different claims, and both should be reported.
* Statistical power must be computed for the contrast that matters. A null at N = 30 became a clear effect at N = 190.

# Related work

* **Steering vectors:**
  * Optimised steering vectors that reproduce target sentences (Subramani et al., 2022).
  * Activation Addition (Turner et al., 2024) and CAA (Rimsky et al., 2024).
  * Inference-Time Intervention (Li et al., 2023) and representation engineering (Zou et al., 2023).
  * Persona vectors as differences of mean activations (Chen et al., 2025).
* **Reliability:** Tan et al. (Tan et al., 2024) show input-dependent and sometimes reversed ("anti-steerable") effects. Our sign asymmetry is a concrete instance.
* **Mechanism:** directional ablation of a refusal direction (Arditi et al., 2024) and sparse-autoencoder feature clamping (Templeton et al., 2024) are causal interventions on single directions.

# Limitations

* **Narrow setting:** one model, layer, vector, prompt distribution and classifier.
* **Metric:** a binary classifier with no neutral class (baseline positivity 0.67–0.75 leaves limited headroom), and it cannot separate sentiment from lexical mention or incoherence.
* **Generation length:** 40-token continuations.
* **Control strength:** isotropic random controls are weaker than an unrelated real steering vector of equal norm.
* **Fidelity:** padding follows the paper, not the 2023 README demo.
* **Post-hoc status:** the lexical analysis is exploratory and needs a pre-registered, lexically controlled metric.

# Conclusion

Under pre-registration with norm-matched controls, the ActAdd "Love" − "Hate" vector on GPT-2-XL reliably increases positive sentiment, by about 0.15 at $\alpha=5$. The effect is non-monotone in $\alpha$, costly in fluency, asymmetric in sign, and substantially lexical. The accompanying explainer shows that a full definition-first derivation of steering vectors can be mechanically grounded: verbatim quotes, computed numbers, and enforced definition order.

# Appendix A: Reproducibility

* **Code, data and logs:** `github.com/BurnyCoder/steering-vectors-explained`. `uv run steering-explainer` runs every phase.
* **Pre-registrations:** commits `7da591f` (Exp. 1) and `23a32f4` (Exp. 2) precede their data.
* **Hardware:** RTX 5070 Laptop GPU (8 GB), PyTorch 2.11 + CUDA 12.8, transformers 5.20; about 3 s per batch of 16 conditions.
* **Seeds:**
  * sampling: seed × 1,000,003 + prompt index;
  * random directions: 1234 + r;
  * bootstrap: 0.

# References

- Turner, A. M. et al. (2024). Steering Language Models With Activation Engineering. arXiv:2308.10248.
- Turner, A. M. et al. (2023). Steering GPT-2-XL by adding an activation vector. LessWrong.
- Rimsky (Panickssery), N. et al. (2024). Steering Llama 2 via Contrastive Activation Addition. ACL 2024.
- Subramani, N., Suresh, N., Peters, M. E. (2022). Extracting Latent Steering Vectors from Pretrained Language Models. Findings of ACL.
- Li, K. et al. (2023). Inference-Time Intervention. NeurIPS 2023.
- Zou, A. et al. (2023). Representation Engineering. arXiv:2310.01405.
- Arditi, A. et al. (2024). Refusal in Language Models Is Mediated by a Single Direction. NeurIPS 2024.
- Templeton, A. et al. (2024). Scaling Monosemanticity. Transformer Circuits Thread.
- Chen, R. et al. (2025). Persona Vectors. arXiv:2507.21509.
- Tan, D. et al. (2024). Analyzing the Generalization and Reliability of Steering Vectors. NeurIPS 2024.
- Park, K., Choe, Y. J., Veitch, V. (2024). The Linear Representation Hypothesis and the Geometry of LLMs. ICML 2024.
- Elhage, N. et al. (2021). A Mathematical Framework for Transformer Circuits.
- Radford, A. et al. (2019). Language Models are Unsupervised Multitask Learners.
- Maas, A. L. et al. (2011). Learning Word Vectors for Sentiment Analysis. ACL.
- Hartmann, J. et al. (2023). More than a Feeling. IJRM 40(1).
- Efron, B., Tibshirani, R. (1993). An Introduction to the Bootstrap.
- Holm, S. (1979). A Simple Sequentially Rejective Multiple Test Procedure. Scand. J. Statist.
- Nosek, B. A. et al. (2018). The preregistration revolution. PNAS 115(11).
