"""log.py — timestamped logging to the terminal *and* to logs/run_<timestamp>.log.

Global context: every phase logs through `get_logger(__name__)`. LLM prompts, completions and
narration text are logged in full (never truncated) so a run can be audited from its log alone.
Docs: logging cookbook, multiple handlers (https://docs.python.org/3/howto/logging-cookbook.html).
"""

import logging  # standard-library logging framework
import sys  # sys.stdout for the live console handler
from datetime import datetime  # timestamp in the log file name
from pathlib import Path  # log directory path

_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"  # time | level | module | text
_configured: Path | None = None  # path of the active log file once configured (module-level singleton)


def setup_logging(log_dir: Path) -> Path:
    """Attach a console handler and a fresh timestamped file handler to the root logger (once)."""
    global _configured
    if _configured is not None:  # idempotent: later calls reuse the same file
        return _configured
    log_dir.mkdir(parents=True, exist_ok=True)  # logs/ is gitignored, create on demand
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252, which cannot print ℓ, α, …
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    path = log_dir / f"run_{datetime.now():%Y%m%d_%H%M%S}.log"  # e.g. logs/run_20261018_150102.log
    root = logging.getLogger()  # root logger: every module logger propagates here
    root.setLevel(logging.INFO)  # INFO and above are recorded
    fmt = logging.Formatter(_FORMAT)  # shared format for both sinks
    for handler in (logging.StreamHandler(sys.stdout), logging.FileHandler(path, encoding="utf-8")):
        handler.setFormatter(fmt)  # same layout on screen and on disk
        root.addHandler(handler)  # register sink
    _configured = path  # remember so repeated setup calls are no-ops
    return path


def get_logger(name: str) -> logging.Logger:
    """Return a module logger; the root handlers set up by `setup_logging` do the writing."""
    return logging.getLogger(name)
