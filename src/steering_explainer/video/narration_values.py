"""narration_values.py — turn the JSON results into the strings spoken in data/script.yaml.

Global context: script beats contain {placeholders}; this pure function computes their values from
data/practical_example.json (steering/example.py) and data/study/summary.json (study/analyze.py),
so the narration can never drift from the measured numbers. Missing study results produce an
explicit "pending" sentence instead of a made-up number.
"""

PENDING = "The study results are pending."


def _tok(s: str) -> str:
    """A token as it should be read aloud: surrounding spaces removed."""
    return s.strip()


def compute(ex: dict, st: dict) -> dict:
    v = {}
    if ex:
        m = ex["model"]
        v["d_model"] = f"{m['d_model']:,}"  # 1,600
        v["n_layers"] = str(m["n_layers"])  # 48
        v["vocab"] = f"{m['d_vocab']:,}"  # 50,257
        v["n_params_b"] = f"{m['n_params'] / 1e9:.1f}"  # ≈ 1.6
        hate_pos = ex["tokens_prompt"].index(" hate")  # position of " hate" in "<|endoftext|>I hate you because"
        v["h_norm_hate"] = f"{ex['h_prompt_norm_per_pos'][hate_pos]:.1f}"
        top = ex["next_token"]["unsteered_top5"][0]
        v["top1_token"], v["top1_prob"] = _tok(top[0]), f"{top[1]:.2f}"
        v["h_plus_norm"], v["h_minus_norm"] = f"{ex['h_plus_norm']:.0f}", f"{ex['h_minus_norm']:.0f}"
        v["cos"] = f"{ex['cos_plus_minus']:.2f}"
        v["hA_norm"] = f"{ex['h_A_norm_per_pos'][1]:.1f}"
        v["gain1"] = _tok(ex["next_token"]["largest_gains"][0][0])
    if st:
        pp = st["means"]["p_pos"]
        p0, p5, r5 = pp["steer_0"][0], pp["steer_5"][0], pp["random_5"][0]
        pr = st["primary"]
        v["n_prompts"] = str(st["n_prompts"])
        v["result_sentence"] = (f"Average positivity was {p0:.2f} without steering and {p5:.2f} at alpha five, "
                                f"while random directions of the same size gave {r5:.2f}.")
        v["verdict_sentence"] = (f"At alpha five, steering minus random is {pr['mean']:+.2f}, with a confidence interval "
                                 f"from {pr['lo']:+.2f} to {pr['hi']:+.2f}, so our pre-registered main hypothesis is "
                                 f"{pr['verdict']}.")
        fl = st["fluency"]
        v["cost_sentence"] = (f"At alpha fifteen it rose by {fl['steer_15']['mean']:.2f} per token, compared with "
                              f"{fl['random_15']['mean']:.2f} for random directions of the same size.")
    else:
        v.update(n_prompts="several hundred", result_sentence=PENDING, verdict_sentence="", cost_sentence="")
    return v
