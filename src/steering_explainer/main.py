"""main.py — the one wrapper that runs the whole project as clearly named phases.

Global context (data flow):
  verify_sources    data/sources.yaml -> download sources -> every quote checked verbatim
  practical_example GPT-2-XL + "Love"−"Hate" -> data/practical_example.json (numbers for the video)
  preregister       settings -> reports/exp01_preregistration.md (written BEFORE any study data)
  pilot             20 pilot prompts -> effect size -> power analysis -> data/study/power.json
  study             N fresh prompts × conditions × seeds -> data/study/main.jsonl (completions + scores)
  analyze           bootstrap CIs, Wilcoxon+Holm, Spearman -> data/study/summary.json + figures
  preregister2      exp01 effect size -> powered N -> reports/exp02_preregistration.md (committed before data)
  replicate         N fresh prompts, primary steer(5) - steer(0) -> data/study/exp02*.json(l) + figures
  posthoc           exploratory, NOT pre-registered: share of completions containing love/hate -> *_posthoc.json
  render            Manim chapters (edge-tts narration) -> media/videos/... (--chapters ch03 --quality l)
  inspect           one contact sheet of frames per chapter -> outputs/check/ (visual QA)
  assemble          ffmpeg concat + chapters + merged subtitles -> outputs/
  docs              data/glossary.yaml + data/sources.yaml -> docs/glossary.md, docs/sources.md
  tables            data/study/*.json -> reports/results_tables.md (generated, never hand-typed)
  paper             reports/paper/paper.md -> reports/paper/paper.pdf (pandoc + xelatex)
Usage: `uv run steering-explainer` (all phases) or `uv run steering-explainer --phases study analyze`.
"""

import argparse
import os
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


def _exp02_n(ctx: Context) -> tuple[int, float, int]:
    """(N, d_z, prompt offset) for experiment 02, derived from experiment 01's steer(5) − steer(0) effect."""
    import json
    from steering_explainer.study import stats
    from steering_explainer.study.analyze import load_records, primary_diff
    _, main_path, power_path, _ = _study_paths(ctx)
    dz = stats.cohens_dz(primary_diff(load_records(main_path), ("steer", 0.0)))
    n1 = json.loads(power_path.read_text(encoding="utf-8"))["chosen_n"]
    return int(min(stats.required_n(dz), ctx.s.n_max)), dz, ctx.s.n_pilot + n1


def preregister2(ctx: Context) -> None:
    from steering_explainer.study.design import exp02_preregistration_markdown, write_preregistration
    n, dz, off = _exp02_n(ctx)
    write_preregistration(ctx.s, "exp02", exp02_preregistration_markdown(ctx.s, n, dz, off))
    log.info("Experiment 02 pre-registered: N=%d (d_z=%.3f), prompts from index %d", n, dz, off)


def replicate(ctx: Context) -> None:
    import json
    from steering_explainer.study.analyze import analyze as run_analysis, write_summary
    from steering_explainer.study.plots import dose_response_figure
    from steering_explainer.study.prompts import imdb_prefixes
    from steering_explainer.study.run import run_prompts
    n, _, off = _exp02_n(ctx)
    d = ctx.s.data_dir / "study"
    prompts = imdb_prefixes(off + n, ctx.s.prompt_words)[off:]  # fresh, disjoint from pilot and exp01
    run_prompts(ctx.s, *ctx.model_tok, _scorer(ctx), prompts, d / "exp02.jsonl")
    summary = run_analysis(ctx.s, d / "exp02.jsonl", ref=("steer", 0.0))
    write_summary(summary, d / "exp02_summary.json")
    log.info("Experiment 02 summary:\n%s", json.dumps(summary, indent=2, ensure_ascii=False))
    dose_response_figure(summary, ctx.s.reports_dir / "figures" / "exp02_dose_response.png", "light", "experiment 02")
    dose_response_figure(summary, d / "exp02_dose_response_dark.png", "dark", "experiment 02")


def posthoc(ctx: Context) -> None:
    from steering_explainer.study.posthoc import write_posthoc
    write_posthoc(ctx.s)
    log.info("Post-hoc (exploratory) lexical analysis written to data/study/*_posthoc.json")


def render(ctx: Context) -> None:
    from steering_explainer.video.render import render_chapters
    render_chapters(ctx.s, ctx.chapters)


def assemble(ctx: Context) -> None:
    from steering_explainer.video.render import assemble as run_assemble
    run_assemble(ctx.s)


def docs(ctx: Context) -> None:
    from steering_explainer.docs_gen import write_docs
    write_docs(ctx.s)
    log.info("Wrote docs/glossary.md and docs/sources.md")


def tables(ctx: Context) -> None:
    from steering_explainer.report import write_results_tables
    write_results_tables(ctx.s)
    log.info("Wrote reports/results_tables.md")


def paper(ctx: Context) -> None:
    from steering_explainer.report import build_paper
    build_paper(ctx.s)


def inspect(ctx: Context) -> None:
    from steering_explainer.video.render import contact_sheets
    log.info("Contact sheets: %s", contact_sheets(ctx.s))


PHASES = {"verify_sources": verify_sources, "practical_example": practical_example, "preregister": preregister,
          "pilot": pilot, "study": study, "analyze": analyze, "preregister2": preregister2, "replicate": replicate, "posthoc": posthoc,
          "render": render, "inspect": inspect, "assemble": assemble, "docs": docs, "tables": tables, "paper": paper}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--phases", nargs="+", choices=list(PHASES), default=list(PHASES), help="phases to run, in order")
    parser.add_argument("--chapters", nargs="*", default=None, help="render only these chapter ids, e.g. ch03 ch07")
    parser.add_argument("--quality", choices=["l", "m", "f", "h", "k"], default=None, help="override RENDER_QUALITY (f = 1080p30)")
    args = parser.parse_args(argv)
    if args.quality:
        os.environ["RENDER_QUALITY"] = args.quality  # load_settings never overrides an already-set variable
    settings = load_settings()  # .env -> Settings (also sets PATH/HF_HOME)
    log_path = setup_logging(settings.root / "logs")
    log.info("Run started; log file %s; phases %s; settings %s", log_path, args.phases, settings)
    ctx = Context(settings)
    ctx.chapters = args.chapters
    for name in args.phases:
        log.info("===== PHASE %s =====", name)
        PHASES[name](ctx)
    log.info("Run finished.")


if __name__ == "__main__":
    main()
