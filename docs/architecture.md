# Architecture

One package, `src/steering_explainer/`, with a single wrapper (`main.py`) that runs clearly named
phases in order. Each phase is a thin function that calls a module; modules never read `.env`
themselves (they receive the frozen `Settings` from `config.py`).

## Modules

| Module | Responsibility |
|---|---|
| `main.py` | CLI wrapper: `--phases`, `--chapters`, `--quality`; one timestamped log per run |
| `config.py` | `.env` → `.env.example` defaults → frozen `Settings`; prepends MiKTeX/Pandoc to `PATH`, pins `HF_HOME` inside the repo |
| `log.py` | console + `logs/run_<timestamp>.log`, UTF-8, nothing truncated |
| `sources.py` | load `data/sources.yaml`; download each source once (`data/cache/sources/`); HTML/PDF → text; verify every quote verbatim |
| `docs_gen.py` | render `docs/glossary.md` and `docs/sources.md` from the YAML files |
| `steering/model.py` | load GPT-2 with Hugging Face `transformers`; tokenize with `<|endoftext|>` prepended (as ActAdd/TransformerLens do) |
| `steering/vectors.py` | `resid_pre` (input of block ℓ), ActAdd `h_A` with right-padding, CAA `mean_difference`, norm-matched `random_like` controls |
| `steering/intervene.py` | forward pre-hook adding `α·v` at absolute positions `< n` (KV-cache safe), per-row α in one batch, TransformerLens-style sampler (temperature → frequency penalty → top-p), completion NLL |
| `steering/example.py` | every real number shown in the video → `data/practical_example.json` |
| `study/design.py` | conditions + the pre-registration documents (`reports/exp0*_preregistration.md`) |
| `study/prompts.py` | deterministic IMDb review prefixes (pilot, exp01, exp02 are disjoint slices) |
| `study/run.py` | one batch per (prompt, seed) holding every condition; JSONL records; resumable |
| `study/score.py` | SiEBERT P(positive) |
| `study/stats.py` | paired bootstrap CI, Wilcoxon, Holm, power (`TTestPower`), per-prompt Spearman |
| `study/analyze.py` | the pre-registered analysis → `summary.json` |
| `study/posthoc.py` | exploratory whole-word love/hate counts + positivity of α = −5 "hate" completions → `*_posthoc.json` |
| `study/plots.py` | dose-response figure (light for reports, dark for the video); redrawn by the `figures` phase |
| `video/theme.py` | colours/fonts; one colour per mathematical role |
| `video/tts_edge.py` | manim-voiceover `SpeechService` for edge-tts with word timings (bookmarks) |
| `video/widgets.py` | `ChapterScene` base (narration beats, citation footer) + reusable components |
| `video/formulas.py` | the two central equations, split into coloured parts |
| `video/toy.py` | exact arithmetic for every toy example |
| `video/narration_values.py` | JSON results → spoken numbers/sentences |
| `video/scenes/chNN_*.py` | one Manim scene per chapter |
| `video/render.py` | render chapters, contact sheets, assemble MP4 + chapters + subtitles + description |

## Invariants (enforced by tests)

* Every quote is verbatim in its source (`tests/test_sources.py`, network test); non-CC-BY quotes ≤ 15 words.
* No narration uses a term before the chapter that defines it (`tests/test_script.py`).
* Scenes speak exactly the beats in `data/script.yaml` (`tests/test_script.py`).
* Toy numbers are computed (`tests/test_toy.py`); real numbers come from JSON produced by code.
* Steering hook: α = 0 is the identity; adds exactly α·v at the front positions only; cached = uncached
  generation (`tests/test_steering.py`).
