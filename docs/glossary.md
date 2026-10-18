# Glossary (generated from data/glossary.yaml)

Every term in the order the video defines it. `chapter` = first chapter whose narration defines it
(enforced by tests/test_script.py).

| Term | Chapter | Definition |
|---|---|---|
| language model | ch00 | A program that continues text by repeatedly predicting the next token. |
| prompt | ch00 | The text given to the model to continue. |
| vector | ch00 | An ordered list of real numbers (formalised in chapter 1). |
| steering vector | ch00 | A vector added inside a model to change its behaviour (formalised in chapters 7-8). |
| scalar | ch01 | A single real number. |
| real number | ch01 | Any number on the continuous number line; their set is ℝ. |
| element of | ch01 | x ∈ S means x belongs to the set S. |
| component | ch01 | One entry of a vector. |
| dimension | ch01 | The number of components d; ℝ^d is the set of all such vectors. |
| parameters | ch01 | The learned numbers that define a model. |
| training | ch01 | The process that learns a model's parameters from data. |
| sigma (sum) | ch02 | Σ: add up every term. |
| mean | ch02 | Sum divided by count: (1/n) Σ x_i. |
| dot product | ch02 | a·b = Σ_i a_i b_i, one scalar. |
| norm | ch02 | Length ‖v‖ = √(v·v). |
| unit vector | ch02 | A vector of norm 1; v/‖v‖ keeps only the direction. |
| function | ch03 | f: X → Y assigns exactly one output in Y to each input in X. |
| token | ch03 | A word or word piece with an integer ID. |
| vocabulary | ch03 | The set V of all tokens; |V| = 50,257 for GPT-2. |
| position | ch03 | A token's index t in the sequence, from 0. |
| embedding | ch03 | Function mapping a token (and its position) to a vector in ℝ^d. |
| layer | ch04 | One of L processing steps; GPT-2-XL has L = 48. |
| attention | ch04 | Sub-layer that moves information between positions. |
| MLP | ch04 | Sub-layer that transforms each position's vector separately. |
| residual stream | ch04 | The running per-position vector that every sub-layer reads from and adds to. |
| activation | ch04 | A number or vector computed inside the model, e.g. h_ℓ^(t). |
| forward pass | ch04 | One run through all layers. |
| matrix | ch05 | A rectangular grid of numbers; times a vector = one dot product per row. |
| logit | ch05 | Unnormalised score per token, z = W_U h. |
| softmax | ch05 | p_i = e^{z_i} / Σ_j e^{z_j}. |
| probability | ch05 | Numbers in [0,1] that sum to 1 over all outcomes. |
| sampling | ch05 | Choosing the next token at random according to the probabilities. |
| linear representation hypothesis | ch06 | Concepts correspond to directions in activation space. |
| contrast pair | ch07 | Two inputs differing mainly in the target concept (p⁺, p⁻). |
| ActAdd | ch07 | Steering with h_ℓ(p⁺) − h_ℓ(p⁻) from a single pair (Turner et al.). |
| CAA | ch07 | Steering with a mean difference over a dataset of triples (Rimsky et al.). |
| dataset | ch07 | A finite set of examples, here triples (p, c⁺, c⁻). |
| completion | ch07 | Text that follows a prompt. |
| mean difference | ch07 | (1/|D|) Σ [a(p,c⁺) − a(p,c⁻)]. |
| cosine similarity | ch07 | Dot product of two unit vectors, in [−1, 1]. |
| steering coefficient | ch08 | Scalar α scaling the added vector; sign sets direction. |
| control | ch09 | A comparison condition identical except for the tested factor. |
| classifier | ch09 | A model that assigns a label or score to text. |
| confidence interval | ch09 | Range of plausible values for an estimate (here 95%, bootstrap). |
| bootstrap | ch09 | Resampling the data with replacement to measure uncertainty. |
| negative log-likelihood | ch09 | −(1/T) Σ log p(token_t | earlier tokens): the model's average surprise. |
| Inference-Time Intervention | ch10 | Shifting activations of selected attention heads (Li et al.). |
| representation engineering | ch10 | Reading and controlling representation directions (Zou et al.). |
| directional ablation | ch10 | x − (r̂·x) r̂: delete the component along r̂. |
| projection | ch10 | (r̂·x) r̂: the part of x along the unit vector r̂. |
| feature | ch10 | A learned direction representing one concept. |
