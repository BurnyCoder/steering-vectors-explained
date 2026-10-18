"""main.py — the one wrapper that runs the whole project as clearly named phases.

Global context (data flow):
  verify_sources    data/sources.yaml -> download sources -> every quote checked verbatim
  practical_example GPT-2-XL + "Love"−"Hate" -> data/practical_example.json (numbers for the video)
  preregister       settings -> reports/exp01_preregistration.md (written BEFORE any study data)
  pilot             20 pilot prompts -> effect size -> power analysis -> data/study/power.json
  study             N fresh prompts × conditions × seeds -> data/study/completions.jsonl (+ scores)
  analyze           bootstrap CIs, Wilcoxon+Holm, Spearman -> data/study/summary.json + figures
  render            Manim chapters (edge-tts narration) -> media/videos/...
  assemble          ffmpeg concat + chapters + merged subtitles -> outputs/
  paper             reports/paper/paper.md -> reports/paper/paper.pdf (pandoc + xelatex)
Usage: `uv run steering-explainer` (all phases) or `uv run steering-explainer --phases study analyze`.
"""

import argparse
from functools import cached_property

from steering_explainer.config import Settings, load_settings
from steering_explainer.log import get_logger, setup_logging

log = get_logger(__name__)


class Context:
    """Shared state for phases; the GPT-2-XL model is loaded lazily, at most once per run."""

    def __init__(self, settings: Settings):
        self.s = settings

    @cached_property
    def model_tok(self):
        from steering_explainer.steering.model import load_model  # heavy import only when needed
        return load_model(self.s.model_name, self.s.device, self.s.dtype)


def verify_sources(ctx: Context) -> None:
    from steering_explainer import sources
    reg = sources.load_sources(ctx.s.data_dir / "sources.yaml")
    missing = sources.verify_quotes(reg, ctx.s.data_dir / "cache" / "sources")
    if missing:
        raise SystemExit(f"Quotes not found verbatim in their sources: {missing}")
    log.info("All %d quotes verified verbatim.", sum(len(s.quotes) for s in reg.values()))


def practical_example(ctx: Context) -> None:
    from steering_explainer.steering.example import run_practical_example
    run_practical_example(ctx.s, *ctx.model_tok)


def _study_paths(ctx: Context):
    d = ctx.s.data_dir / "study"
    return d / "pilot.jsonl", d / "main.jsonl", d / "power.json", d / "summary.json"


def _prompts(ctx: Context, n_main: int):
    from steering_explainer.study.prompts import imdb_prefixes
    allp = imdb_prefixes(ctx.s.n_pilot + n_main, ctx.s.prompt_words)
    return allp[: ctx.s.n_pilot], allp[ctx.s.n_pilot:]  # disjoint pilot / main sets


def _scorer(ctx: Context):
    from steering_explainer.study.score import SentimentScorer
    return SentimentScorer(ctx.s.sentiment_model, ctx.s.device)


def preregister(ctx: Context) -> None:
    from steering_explainer.study.design import write_preregistration
    write_preregistration(ctx.s)  # committed to git before pilot/study data exist
    log.info("Pre-registration written to %s", ctx.s.reports_dir / "exp01_preregistration.md")


def pilot(ctx: Context) -> None:
    import json
    from steering_explainer.study import stats
    from steering_explainer.study.analyze import load_records, primary_diff
    from steering_explainer.study.run import run_prompts
    pilot_path, _, power_path, _ = _study_paths(ctx)
    pilot_prompts, _ = _prompts(ctx, 0)
    run_prompts(ctx.s, *ctx.model_tok, _scorer(ctx), pilot_prompts, pilot_path)
    d = primary_diff(load_records(pilot_path))
    dz = stats.cohens_dz(d)
    n_req = stats.required_n(dz) if dz != float("inf") else ctx.s.n_min
    n = int(min(max(n_req, ctx.s.n_min), ctx.s.n_max))
    power = {"pilot_n": len(d), "pilot_mean_diff": float(d.mean()), "pilot_dz": dz, "required_n_80pct": n_req, "chosen_n": n}
    power_path.write_text(json.dumps(power, indent=2), encoding="utf-8")
    log.info("Power analysis: %s", power)


def study(ctx: Context) -> None:
    import json
    from steering_explainer.study.run import run_prompts
    _, main_path, power_path, _ = _study_paths(ctx)
    n = json.loads(power_path.read_text(encoding="utf-8"))["chosen_n"]
    _, main_prompts = _prompts(ctx, n)
    log.info("Main study on %d fresh prompts", len(main_prompts))
    run_prompts(ctx.s, *ctx.model_tok, _scorer(ctx), main_prompts, main_path)


def analyze(ctx: Context) -> None:
    import json
    from steering_explainer.study.analyze import analyze as run_analysis, write_summary
    from steering_explainer.study.plots import dose_response_figure
    _, main_path, _, summary_path = _study_paths(ctx)
    summary = run_analysis(ctx.s, main_path)
    write_summary(summary, summary_path)
    log.info("Study summary:\n%s", json.dumps(summary, indent=2, ensure_ascii=False))
    dose_response_figure(summary, ctx.s.reports_dir / "figures" / "exp01_dose_response.png", "light")
    dose_response_figure(summary, ctx.s.data_dir / "study" / "dose_response_dark.png", "dark")


PHASES = {"verify_sources": verify_sources, "practical_example": practical_example, "preregister": preregister,
          "pilot": pilot, "study": study, "analyze": analyze}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--phases", nargs="+", choices=list(PHASES), default=list(PHASES), help="phases to run, in order")
    args = parser.parse_args(argv)
    settings = load_settings()  # .env -> Settings (also sets PATH/HF_HOME)
    log_path = setup_logging(settings.root / "logs")
    log.info("Run started; log file %s; phases %s; settings %s", log_path, args.phases, settings)
    ctx = Context(settings)
    for name in args.phases:
        log.info("===== PHASE %s =====", name)
        PHASES[name](ctx)
    log.info("Run finished.")


if __name__ == "__main__":
    main()
