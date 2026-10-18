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


PHASES = {"verify_sources": verify_sources, "practical_example": practical_example}


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
