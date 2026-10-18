"""conftest.py — load settings once so HF_HOME/PATH point inside the repo before any test imports torch/HF."""

from steering_explainer.config import load_settings

load_settings()  # side effects: HF_HOME=.cache/hf, MiKTeX/Pandoc on PATH
