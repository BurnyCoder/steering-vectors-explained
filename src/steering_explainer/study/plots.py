"""plots.py — dose-response figure (positivity and fluency vs α) for the report and the video.

Global context: one function draws both a light version (report/paper) and a dark version
(video chapter 09, same surface colour as the Manim background). Colours: categorical slots 1-2 of
the validated reference palette (blue = steered, orange = random control), checked with the
dataviz validator for both modes. No truncated probability axis (0-1), no dual axes, error bars =
95% percentile-bootstrap CIs of each condition's mean over prompts (not of paired differences);
random controls are drawn 0.6 to the right of their α so they never hide behind the steered points,
and the legend says so. Docs: matplotlib errorbar
(https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.errorbar.html).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # file output only, no GUI backend
import matplotlib.pyplot as plt

THEMES = {  # surface, primary text, secondary text, grid, steered, random, baseline
    "light": dict(bg="#fcfcfb", fg="#0b0b0b", fg2="#52514e", grid="#e4e3df", steer="#2a78d6", rand="#eb6834", base="#8a8984"),
    "dark": dict(bg="#1a1a19", fg="#f0efec", fg2="#c3c2b7", grid="#3a3a38", steer="#3987e5", rand="#d95926", base="#9a998f"),
}


def _series(means: dict, kind: str):
    """Sorted (alphas, means, lower errors, upper errors) for one condition kind."""
    pts = sorted((float(k.split("_")[1]), v) for k, v in means.items() if k.startswith(kind + "_"))
    xs = [a for a, _ in pts]
    ys = [v[0] for _, v in pts]
    return xs, ys, [v[0] - v[1] for _, v in pts], [v[2] - v[0] for _, v in pts]


def dose_response_figure(summary: dict, path: Path, theme: str = "light", title: str = "", layer: int = 6,
                         n_random: int = 5) -> None:
    """Two panels (positivity, NLL) vs α; `layer` / `n_random` label the run's settings (config.Settings)."""
    t = THEMES[theme]
    dodge_r = 0.6  # x-offset of the random-control markers
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), facecolor=t["bg"])
    panels = [("p_pos", "P(positive) of completion", (0, 1)), ("nll", "Completion NLL (nats/token)", None)]
    for ax, (metric, ylabel, ylim) in zip(axes, panels):
        ax.set_facecolor(t["bg"])
        m = summary["means"][metric]
        for kind, color, label, ls, dodge in (("steer", t["steer"], '"Love" − "Hate" vector', "-", 0.0),
                                              ("random", t["rand"], f"random direction, same norm (mean of {n_random};"
                                               f" drawn at α + {dodge_r:g})", "none", dodge_r)):
            xs, ys, lo, hi = _series(m, kind)
            ax.errorbar([x + dodge for x in xs], ys, yerr=[lo, hi], color=color, lw=2, ls=ls, marker="o", ms=8,
                        capsize=4, mec=t["bg"], mew=2, label=label, zorder=3)  # dodge: controls never hide behind steered points
        ax.set_xticks(_series(m, "steer")[0])  # ticks exactly at the tested α values
        base = m["steer_0"][0]
        ax.axhline(base, color=t["base"], lw=1, ls="--", zorder=1)  # unsteered (α = 0) reference
        ax.annotate("unsteered (α = 0)", xy=(1, base), xycoords=("axes fraction", "data"), xytext=(-4, 4),
                    textcoords="offset points", ha="right", color=t["fg2"], fontsize=9)
        if ylim:
            ax.set_ylim(*ylim)
        else:
            ax.set_ylim(bottom=0)
        ax.set_xlabel("steering coefficient α", color=t["fg"])
        ax.set_ylabel(ylabel, color=t["fg"])
        ax.tick_params(colors=t["fg2"])
        ax.grid(True, color=t["grid"], lw=0.8)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(t["grid"])
    axes[0].legend(loc="lower left", frameon=False, labelcolor=t["fg"])
    fig.suptitle(f"GPT-2-XL, layer {layer} · mean over {summary['n_prompts']} prompts × {len(summary['seeds'])} seeds · bars: 95% bootstrap CI"
                 + (f" · {title}" if title else ""), color=t["fg2"], fontsize=10)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, facecolor=t["bg"])
    plt.close(fig)
