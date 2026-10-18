"""narration_values.py — turn the JSON results into the strings spoken in data/script.yaml.

Global context: script beats contain {placeholders}; this pure function computes their values from
data/practical_example.json (steering/example.py), data/study/summary.json (experiment 01) and
data/study/exp02_summary.json (experiment 02, pre-registered replication). Sentence variants are
chosen by the data (e.g. where positivity peaks, whether α = −5 lowered it), never by hand.
Missing results produce an explicit "pending" sentence instead of a made-up number.
"""

PENDING = "The study results are pending."


def _tok(s: str) -> str:
    """A token as it should be read aloud: surrounding spaces removed."""
    return s.strip()


def _example_values(ex: dict) -> dict:
    m = ex["model"]
    hate_pos = ex["tokens_prompt"].index(" hate")  # position of " hate" in "<|endoftext|>I hate you because"
    top = ex["next_token"]["unsteered_top5"][0]
    return {"d_model": f"{m['d_model']:,}", "n_layers": str(m["n_layers"]), "vocab": f"{m['d_vocab']:,}",
            "n_params_b": f"{m['n_params'] / 1e9:.2f}", "h_norm_hate": f"{ex['h_prompt_norm_per_pos'][hate_pos]:.1f}",
            "top1_token": _tok(top[0]), "top1_prob": f"{top[1]:.2f}", "layer": str(ex["layer"]), "coeff": f"{ex['coeff']:g}",
            "h_plus_norm": f"{ex['h_plus_norm']:.1f}", "h_minus_norm": f"{ex['h_minus_norm']:.1f}",  # same precision as ch07's screen
            "cos": f"{ex['cos_plus_minus']:.2f}", "hA_norm": f"{ex['h_A_norm_per_pos'][1]:.1f}",
            "gain1": _tok(ex["next_token"]["largest_gains"][0][0])}


WORDS = "zero one two three four five six seven eight nine ten".split()  # small counts read better as words


def _word(n: int) -> str:
    return WORDS[n] if 0 <= n < len(WORDS) else str(n)


def _alphas(means: dict, kind: str) -> list[float]:
    """Sorted α values of one condition kind ("steer" / "random") present in a summary's means."""
    return sorted(float(k.split("_")[1]) for k in means if k.startswith(kind + "_"))


def design(st: dict) -> dict:
    """Continuations per prompt and how they split into steered α values and random-direction controls."""
    per, seeds = st["n_completions"] // st["n_prompts"], len(st["seeds"])
    steer, rand = _alphas(st["means"]["p_pos"], "steer"), _alphas(st["means"]["p_pos"], "random")
    return {"per_prompt": per, "seeds": seeds, "steer": steer, "rand": rand,
            "n_dirs": (per // seeds - len(steer)) // len(rand)}  # rows per seed = |steer α| + n_dirs·|random α|


def _study_values(st1: dict, st2: dict) -> dict:
    pp = st2["means"]["p_pos"]
    steer = {float(k.split("_")[1]): v[0] for k, v in pp.items() if k.startswith("steer_")}
    peak = max(steer, key=steer.get)  # α with the highest mean positivity (a description of means, not a test)
    top = max(steer)  # largest α tested
    pr2 = st2["primary"]
    h1_2 = next(t for t in st2["secondary"] if t["contrast"] == "steer_5 - random_5")
    neg = st2["h3_sign"]
    dz = design(st2)
    both = st1["primary"]["lo"] > 0 and h1_2["lo"] > 0  # steer − random CI above 0 in exp01 (primary) and exp02 (secondary)
    vs_random = "steering beat random directions in both runs" if both else "steering did not reliably beat random directions"
    held = {"supported": "held", "falsified": "failed"}  # pre-registered H2 verdicts -> spoken words
    h2 = (f"Our planned test of a steady rise with alpha {held[st1['h2_spearman']['verdict']]} in the first run and "
          f"{held[st2['h2_spearman']['verdict']]} in the second.")
    shape = (f"But more is not always better: average positivity was highest at alpha {peak:g} and lower again at {top:g}."
             if peak < top else f"Average positivity was highest at the largest alpha, {top:g}.")
    sign = ("And the negative alpha did not make text less positive."
            if neg["mean"] >= 0 or neg["p_holm"] >= 0.05 else "A negative alpha made text less positive.")
    cost, cost_r = st2["fluency"][f"steer_{top:g}"]["mean"], st2["fluency"].get(f"random_{top:g}", {}).get("mean")
    return {
        "design_sentence": (f"A first run used {st1['n_prompts']} openings of real movie reviews; a second run, sized "
                            f"using the first, used {st2['n_prompts']} new ones. Each opening got {dz['per_prompt']} "
                            f"continuations: {_word(dz['seeds'])} at each of {_word(len(dz['steer']))} values of alpha, and "
                            f"{_word(dz['seeds'])} for each of {_word(dz['n_dirs'])} random directions at alpha "
                            + " and ".join(f"{a:g}" for a in dz["rand"]) + "."),
        "result_sentence": (f"In the larger run, average positivity was {steer[0.0]:.2f} without steering and "
                            f"{steer[5.0]:.2f} at alpha five, while random directions of the same size gave "
                            f"{pp['random_5'][0]:.2f}."),
        "verdict_sentence": (f"Steering minus no steering at alpha five is {pr2['mean']:+.2f}, with an interval from "
                             f"{pr2['lo']:+.2f} to {pr2['hi']:+.2f}: our main hypothesis is {pr2['verdict']}, and "
                             f"{vs_random}. {h2} {shape} {sign}"),
        "cost_sentence": (f"At alpha {top:g} it was {abs(cost):.2f} nats per token {'higher' if cost > 0 else 'lower'} than "
                          f"without steering" + (f", compared with {cost_r:.2f} for random directions of the same size."
                                                 if cost_r is not None else ".")),
    }


def _toy_values() -> dict:
    """Spoken toy numbers, computed by video/toy.py (pinned by tests/test_toy.py)."""
    from steering_explainer.video import toy
    p = toy.softmax([2, 1, 0])
    st = toy.steering_toy()
    return {"norm_b": f"{toy.norm(toy.B):.2f}", "softmax_210": f"{p[0]:.3f}, {p[1]:.3f} and {p[2]:.3f}",
            "toy_love_before": f"{st['p_before'][0]:.2f}", "toy_love_after": f"{st['p_after'][0]:.2f}"}


def _pct(x: float) -> str:
    return "under 1 percent" if x < 0.01 else f"{x * 100:.0f} percent"


def _posthoc_values(ph: dict) -> dict:
    """Exploratory (not pre-registered) lexical finding from study/posthoc.py, announced as unplanned.

    The interpretation ("inserts the words more than the sentiment") rests on the stored positivity of the
    α = −5 completions that say "hate" versus unsteered completions; both numbers are spoken so it can be judged.
    """
    r = ph["rates"]
    return {"posthoc_sentence": (f"A check we did not plan in advance suggests the vector inserts the words more than the "
                                 f"sentiment: at minus five, {_pct(r['steer_-5']['hate'][0])} of continuations contain the word "
                                 f"hate, versus {_pct(r['steer_0']['hate'][0])} without steering, yet they average "
                                 f"{ph['hate_at_minus5_positivity']:.3f} positivity, versus {ph['unsteered_positivity']:.3f} "
                                 f"unsteered. At plus five, {_pct(r['steer_5']['love'][0])} contain love, versus "
                                 f"{_pct(r['steer_0']['love'][0])} without steering.")}


def compute(ex: dict, st1: dict, st2: dict | None = None, ph: dict | None = None) -> dict:
    v = _toy_values() | (_example_values(ex) if ex else {})
    if st1 and st2:
        v.update(_study_values(st1, st2))
    else:
        v.update(design_sentence="", result_sentence=PENDING, verdict_sentence="", cost_sentence="")
    v.update(_posthoc_values(ph) if ph else {"posthoc_sentence": ""})
    return v
