# Summary of all experiments (plain language)

*Author: Libor Burian (independent researcher). Full details: [all_experiments.md](all_experiments.md).*

## Key terms
| Term | Meaning in one line |
|---|---|
| Language model | A program that continues text one token (word piece) at a time. |
| Activation / residual stream | The list of numbers (vector) the model keeps for each token while it reads; layers add to it. |
| Steering vector | A vector added to those activations to change what the model writes. Weights are not changed. |
| ActAdd | Steering vector = activations for one prompt minus activations for a contrasting prompt ("Love" − "Hate"). |
| Coefficient α | How hard we push: 0 = off, bigger = stronger, negative = the opposite direction. |
| Random control | A push of exactly the same size in a random direction, to check the direction matters. |
| P(positive) | A separate classifier's probability that a text is positive (0 to 1). |
| NLL (fluency cost) | How surprised the original model is by the text; higher = less natural. |
| 95% confidence interval | The range in which the true average plausibly lies (bootstrap over prompts). |
| Pre-registration | Writing hypotheses and analysis down, and committing them, before collecting data. |
| d_z / power analysis | Effect size in standard-deviation units / choosing a sample size big enough to detect it. |

## Models used
| Model | Architecture | Training objective / data (by its authors) | Role here | Trained by us? |
|---|---|---|---|---|
| GPT-2-XL (Radford et al. 2019) | decoder-only transformer, 48 layers, d = 1600, 1.56 B parameters, vocabulary 50,257 | next-token prediction on WebText | the model being steered | no (frozen) |
| SiEBERT (Hartmann et al. 2023) | RoBERTa-large classifier | binary sentiment, fine-tuned on 15 datasets | judge of positivity | no (frozen) |

No network was trained or fine-tuned in this project. Steering is an inference-time edit, so there is no
training curriculum, loss or checkpoint to upload.

## Experiments at a glance
| Experiment | Prompts | Main comparison | Result | In plain words |
|---|---|---|---|---|
| Practical example | "I hate you because" | unsteered vs. steered (seed 0) | steered text turns to love | the demo reproduces |
| 01 | 30 movie-review openings | steered vs. random push (α = 5) | +0.125 [0.045, 0.203] | the direction matters, not just the push |
| 02 | 190 new openings | steered vs. no steering (α = 5) | +0.146 [0.102, 0.192] | steering works on average, about +15 points of positivity |
| 02 | same | α = −5 vs. 0 | +0.052 [−0.000, 0.105] | reversing the vector did *not* make text negative |
| 02 | same | fluency at α = 15 | +1.38 nats/token | strong steering makes text less natural |
| post-hoc | same | word counts | "love" in 62.5% at α = 5; "hate" in 29.5% at α = −5 | the vector largely injects the words themselves |
