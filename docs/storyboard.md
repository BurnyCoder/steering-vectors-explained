# Storyboard

The narration itself lives only in [`data/script.yaml`](../data/script.yaml) (with `{placeholders}` filled
from measured results); this page describes the structure. Terms and where they are defined:
[`docs/glossary.md`](glossary.md). Quotes: [`docs/sources.md`](sources.md).

| # | Chapter | Defines | Simplest worked example | Practical example (real data) |
|---|---|---|---|---|
| 00 | Hook | language model, prompt, vector, steering vector (informally) | — | GPT-2-XL "I hate you because" unsteered vs. steered, seed 0 |
| 01 | Numbers and vectors | scalar, ℝ, ∈, vector, component, dimension d, ℝ^d, parameters, training | (2, 1) ∈ ℝ² as an arrow | d = 1600, ≈1.56 B parameters (model config) |
| 02 | Vector arithmetic | +, scalar ×, −, Σ, mean, dot product, norm, unit vector | a = (1, 2), b = (3, −1): a+b, 2b, a−b, a·b = 1, ‖b‖ = √10 | — |
| 03 | Text → vectors | function, tokenizer, token, vocabulary V, \|V\|, position t, embedding | 3-token toy embedding | real GPT-2 tokens + IDs; \|V\| = 50,257 |
| 04 | Layers and the residual stream | layer ℓ, L, attention, MLP, residual stream, activation h_ℓ^(t), forward pass | 2-D stream (1,0) → (1,1) → (1.5, 0.5) | L = 48; ‖h₆‖ at "hate" |
| 05 | Vectors → words | matrix, W_U, logits, softmax, probability, sampling | softmax(2,1,0) = (0.665, 0.245, 0.090) | real next-token top 5 |
| 06 | Concepts as directions | linear representation hypothesis | 2-D "positivity" axis; illustrative king/queen picture | Mikolov et al., Park et al. quotes; caveats: Nissim et al. 2020 (analogy search), Engels et al. 2024 (circular features) |
| 07 | Building the steering vector | contrast pair, ActAdd h_A, CAA, dataset D of triples, a_ℓ, \|D\|, mean difference, cosine similarity | three 2-D differences average to (2, 0) | real "Love"/"Hate" norms, cosine, h_A |
| 08 | Applying it | h̃ = h + αv, steering coefficient α, positions T | h = (1,1), v = (2,0), α = 1.5 → probabilities before/after | real probability shift + completions |
| 09 | Does it really work? | control, classifier, confidence interval, bootstrap, negative log-likelihood | — | experiments 01 and 02 (pre-registered) |
| 10 | Nuances and relatives | Inference-Time Intervention, representation engineering, directional ablation, projection, feature | 2-D projection picture | verified quotes (ActAdd incl. layer choice, Tan et al., Li et al., Zou et al., Arditi et al., Templeton et al.) |
| 11 | Recap | — (every symbol annotated with its set and meaning) | — | — |

Visual conventions: one colour per role (steering vector orange, α yellow, residual stream blue,
p⁺/c⁺ green, p⁻/c⁻ red, sets violet); a citation footer appears whenever a slide makes a sourced claim.
