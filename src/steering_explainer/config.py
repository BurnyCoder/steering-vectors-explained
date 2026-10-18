"""config.py — load every pipeline setting from `.env` (overrides) and `.env.example` (defaults).

Global context: every phase (steering experiment, study, video render) receives one frozen
`Settings` object, so no module reads environment variables on its own and defaults live in
exactly one place (`.env.example`).
Docs: python-dotenv `load_dotenv(override=False)` keeps already-set variables
(https://github.com/theskumar/python-dotenv#readme); dataclasses (https://docs.python.org/3/library/dataclasses.html).
"""

import os  # read environment variables and expand %LOCALAPPDATA%-style paths
from dataclasses import dataclass  # frozen dataclass = immutable, hashable settings record
from pathlib import Path  # OS-independent paths

from dotenv import load_dotenv  # parses KEY=VALUE files into os.environ

# Project root = three levels up from this file: src/steering_explainer/config.py -> repo root.
ROOT = Path(__file__).resolve().parents[2]


def _floats(raw: str) -> tuple[float, ...]:
    """Parse a comma-separated list such as "-5,0,2" into a tuple of floats."""
    return tuple(float(x) for x in raw.split(",") if x.strip())  # skip empty items from trailing commas


def _ints(raw: str) -> tuple[int, ...]:
    """Parse a comma-separated list such as "0,1,2" into a tuple of ints."""
    return tuple(int(x) for x in raw.split(",") if x.strip())


@dataclass(frozen=True)
class Settings:
    """All tunables; field names mirror the upper-case keys in `.env.example`."""

    root: Path  # repository root, used to resolve data/, outputs/, logs/
    model_name: str  # Hugging Face id of the steered model (gpt2-xl)
    device: str  # "cuda" or "cpu"
    dtype: str  # torch dtype name, e.g. "float16"
    steer_layer: int  # ℓ: the block whose *input* residual stream is edited
    steer_coeff: float  # α used for the practical example (ActAdd's +5)
    prompt_plus: str  # p⁺ of the contrast pair ("Love")
    prompt_minus: str  # p⁻ of the contrast pair ("Hate")
    example_prompt: str  # user prompt of the practical example
    temperature: float  # softmax temperature for sampling
    top_p: float  # nucleus-sampling mass
    freq_penalty: float  # TransformerLens-style additive frequency penalty
    max_new_tokens: int  # completion length in tokens
    alphas: tuple[float, ...]  # study grid of steering coefficients
    random_alphas: tuple[float, ...]  # coefficients at which random-direction controls run
    n_random: int  # R: number of random control directions
    seeds: tuple[int, ...]  # sampling seeds (independent completions per prompt)
    n_pilot: int  # pilot prompts used only for the power analysis
    n_min: int  # floor on the main-study sample size
    n_max: int  # cap on the main-study sample size
    prompt_words: int  # words kept from each IMDb review to form a prompt prefix
    sentiment_model: str  # HF id of the sentiment classifier used as the primary metric
    bootstrap_resamples: int  # number of paired-bootstrap resamples for CIs
    tts_voice: str  # edge-tts voice short name
    tts_rate: str  # edge-tts speaking-rate offset, e.g. "+0%"
    render_quality: str  # manim -q flag letter

    @property
    def data_dir(self) -> Path:
        return self.root / "data"  # committed inputs + small JSON results

    @property
    def outputs_dir(self) -> Path:
        return self.root / "outputs"  # final video, subtitles, description

    @property
    def reports_dir(self) -> Path:
        return self.root / "reports"  # experiment write-ups + paper


def _apply_env_side_effects() -> None:
    """Prepend EXTRA_PATH tool folders to PATH and make HF_HOME absolute inside the repo."""
    extra = os.path.expandvars(os.environ.get("EXTRA_PATH", ""))  # expand %LOCALAPPDATA% on Windows
    dirs = [d for d in extra.split(";") if d and Path(d).is_dir()]  # keep only folders that exist
    if dirs:  # prepend so freshly installed MiKTeX/Pandoc win even if this shell predates the install
        os.environ["PATH"] = os.pathsep.join(dirs + [os.environ.get("PATH", "")])
    hf_home = Path(os.environ.get("HF_HOME", ".cache/hf"))  # HF cache root (models, datasets)
    os.environ["HF_HOME"] = str(hf_home if hf_home.is_absolute() else ROOT / hf_home)  # pin inside repo


def load_settings() -> Settings:
    """Read `.env` then `.env.example` into os.environ and build the frozen Settings."""
    load_dotenv(ROOT / ".env", override=False)  # user overrides first
    load_dotenv(ROOT / ".env.example", override=False)  # defaults fill whatever is still unset
    _apply_env_side_effects()  # PATH + HF_HOME must be set before torch/transformers/manim run
    e = os.environ  # short alias for the lookups below
    return Settings(
        root=ROOT,
        model_name=e["MODEL_NAME"],
        device=e["DEVICE"],
        dtype=e["DTYPE"],
        steer_layer=int(e["STEER_LAYER"]),
        steer_coeff=float(e["STEER_COEFF"]),
        prompt_plus=e["PROMPT_PLUS"],
        prompt_minus=e["PROMPT_MINUS"],
        example_prompt=e["EXAMPLE_PROMPT"],
        temperature=float(e["TEMPERATURE"]),
        top_p=float(e["TOP_P"]),
        freq_penalty=float(e["FREQ_PENALTY"]),
        max_new_tokens=int(e["MAX_NEW_TOKENS"]),
        alphas=_floats(e["ALPHAS"]),
        random_alphas=_floats(e["RANDOM_ALPHAS"]),
        n_random=int(e["N_RANDOM"]),
        seeds=_ints(e["SEEDS"]),
        n_pilot=int(e["N_PILOT"]),
        n_min=int(e["N_MIN"]),
        n_max=int(e["N_MAX"]),
        prompt_words=int(e["PROMPT_WORDS"]),
        sentiment_model=e["SENTIMENT_MODEL"],
        bootstrap_resamples=int(e["BOOTSTRAP_RESAMPLES"]),
        tts_voice=e["TTS_VOICE"],
        tts_rate=e["TTS_RATE"],
        render_quality=e["RENDER_QUALITY"],
    )
