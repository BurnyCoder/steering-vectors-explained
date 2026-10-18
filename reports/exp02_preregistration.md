# Experiment 02 — Pre-registration: powered replication, steered vs. unsteered

*Written and committed after experiment 01 and before any experiment-02 data. Author: Libor Burian (independent researcher).*

## Why
Experiment 01 (N = 30) supported H1 (steered beats same-norm random directions at α = 5), but the contrast
steered(α = 5) − unsteered(α = 0) was small and not significant: d_z = 0.205. That contrast is the one a user of
steering cares about, so this experiment powers it.

## Primary hypothesis and falsification
* **H1′:** P_pos(steer, α = 5) > P_pos(steer, α = 0).
* **Falsified** if the 95% paired-bootstrap CI of the per-prompt mean difference includes 0 or lies below 0.

## Design (identical to experiment 01 except where stated)
* Same model, vector, layer, conditions (α ∈ [-5.0, 0.0, 2.0, 5.0, 10.0, 15.0], random controls at [5.0, 15.0], R = 5),
  sampling settings, seeds [0, 1, 2], metrics and secondary analyses (exp01 H1-H4 re-tested, Holm-corrected).
* **N = 190** fresh prompts: required n for 80% power at two-sided α = 0.05 for d_z = 0.205 (statsmodels TTestPower),
  capped at 200. Prompts are IMDb test prefixes number 50…239 of the same seeded,
  alternating list, i.e. disjoint from the pilot and from experiment 01.
* Anything not listed here is reported as **post-hoc**.
