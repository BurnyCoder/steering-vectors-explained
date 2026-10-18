"""test_narration_values.py — the spoken sentences must say what the data and the screen say.

Global context: video/narration_values.py fills data/script.yaml placeholders from the committed JSON results.
These tests pin the fact-check fixes (docs/fact_check.md): the design sentence counts every continuation
(random controls included), spoken numbers use the same precision as the screen, NLL has a unit, and the
pre-registered dose-response hypothesis (H2) is reported for both runs.
"""

import json

from steering_explainer.config import ROOT
from steering_explainer.video import narration_values as nv

_load = lambda p: json.loads((ROOT / "data" / p).read_text(encoding="utf-8"))  # committed result files
EX, ST1, ST2, PH = (_load(p) for p in ("practical_example.json", "study/summary.json", "study/exp02_summary.json",
                                       "study/exp02_posthoc.json"))
V = nv.compute(EX, ST1, ST2, PH)


def test_design_sentence_counts_every_continuation():
    per_prompt = ST2["n_completions"] // ST2["n_prompts"]  # 48: 6 alphas + 2 x 5 random directions, x 3 seeds
    assert f"{per_prompt} continuations" in V["design_sentence"]
    assert "five random directions" in V["design_sentence"]


def test_spoken_numbers_use_the_screen_precision():
    assert V["h_plus_norm"] == f"{EX['h_plus_norm']:.1f}" and V["h_minus_norm"] == f"{EX['h_minus_norm']:.1f}"
    assert V["n_params_b"] == f"{EX['model']['n_params'] / 1e9:.2f}"  # screen shows "about 1.56 billion"


def test_cost_sentence_states_its_unit():
    assert "nats per token" in V["cost_sentence"]


def test_dose_response_hypothesis_is_reported_for_both_runs():
    held = {"supported": "held", "falsified": "failed"}
    assert (f"{held[ST1['h2_spearman']['verdict']]} in the first run and {held[ST2['h2_spearman']['verdict']]} "
            "in the second") in V["verdict_sentence"]


def test_posthoc_sentence_uses_the_whole_word_rates():
    r = PH["rates"]
    assert f"{nv._pct(r['steer_-5']['hate'][0])} of continuations contain the word hate" in V["posthoc_sentence"]
    assert f"{PH['hate_at_minus5_positivity']:.3f}" in V["posthoc_sentence"]
