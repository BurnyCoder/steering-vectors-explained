# Experiment 02 — Powered replication: is steering better than not steering?

*Author: Libor Burian (independent researcher). Pre-registration: [exp02_preregistration.md](exp02_preregistration.md)
(committed in `23a32f4` before any experiment-02 data).
All numbers: [results_tables.md](results_tables.md) (generated from `data/study/exp02_summary.json`).
Raw completions: `data/study/exp02.jsonl`.*

## Why
[Experiment 01](exp01_love_hate_dose_response.md) left the practically important contrast open. That contrast
is steered(α = 5) − unsteered(α = 0), measured at d_z = 0.205 with N = 30.

## Design
Identical to experiment 01, except for three things:
* The primary contrast is steered(5) − unsteered(0).
* **N = 190 fresh prompts**: IMDb prefixes 50-239, disjoint from the pilot and from experiment 01. N is the
  required sample size for 80% power at d_z = 0.205.
* Experiment 01's H1 (steered − random at α = 5) is re-tested as a secondary, inside the Holm family.

## Results (pre-registered)
| Hypothesis | Estimate [95% CI] | Verdict |
|---|---|---|
| **H1′ primary:** steer(5) − steer(0) | +0.146 [+0.102, +0.192], d_z = 0.459 | **supported** |
| exp01-H1 re-test: steer(5) − random(5) | +0.132 [+0.097, +0.166], Holm p = 1.2e−11 | replicated |
| H2: monotone dose-response (mean ρ) | +0.164 [+0.101, +0.226] | supported |
| H3: α = −5 lowers positivity | +0.052 [−0.000, +0.105] (wrong sign), Holm p = 0.47 | falsified |
| H4: NLL(15) − NLL(0) | +1.380 [+1.332, +1.430] | supported |

More detail:
* **Every positive α beats unsteered** after Holm correction:
  * α = 2: +0.101;
  * α = 5: +0.146;
  * α = 10: +0.168;
  * α = 15: +0.109.
* **The dose-response rises and then falls.** Mean positivity peaks at α = 10 (0.833) and declines at
  α = 15 (0.774). So H2's rank correlation holds on average, but the relation is not monotone at the top.
* **Each seed alone** excludes 0 for the primary contrast: +0.146, +0.116, +0.177.
* **Fluency cost grows with |α|** and exceeds the random control at equal norm:
  * α = 15: +1.38 nats/token (random: +0.74);
  * α = 5: +0.37 (random: +0.36).

![Experiment 02 dose-response](figures/exp02_dose_response.png)

## Post-hoc (exploratory, not pre-registered)
The H3 failure prompted a reading of the completions. Mechanically, the vector also injects the *words*:
* **"lov…" share:** 62.5% of α = +5 completions, versus 5.6% unsteered.
* **"hate" share:** 29.5% of α = −5 completions contain "hate", "hating" or "hatred", versus 0.4% unsteered.
* The α = −5 texts are often incoherent (NLL +1.25) rather than negative, e.g. "ThisHateLove.com is the
  first place…", and the classifier rates many of them positive.

So at layer 6, the front-position "Love" − "Hate" vector behaves partly as a lexical/topic injection, as in
ActAdd's "wedding" topic vectors, and not only as a sentiment direction. The positivity gain is therefore
confounded with mentioning "love". A confirmatory test would need a pre-registered lexical-controlled metric,
e.g. sentiment of completions with the steering words masked.

## Learnings
* Powering the contrast you care about changes the conclusion: "not significant" at N = 30 became
  +0.146 [0.102, 0.192] at N = 190.
* A sign flip is not guaranteed to reverse an effect. −α·v is not "anti-love", it is "+Hate token identity".
  This matches Tan et al. (2024): steerability is input- and concept-dependent and can even reverse.
* The metric's validity limits the claim. A binary sentiment classifier cannot separate "positive" from
  "mentions love" or from "incoherent".
