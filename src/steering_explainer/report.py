"""report.py — build the PDF paper from reports/paper/paper.md with Pandoc + XeLaTeX (MiKTeX).

Global context: the paper is written in Markdown (reviewable on GitHub) and compiled to PDF here.
XeLaTeX is used for Unicode text; Cambria/Cambria Math are Windows system fonts that cover the
symbols used. Pandoc manual: https://pandoc.org/MANUAL.html#creating-a-pdf
"""

import subprocess

from steering_explainer.config import Settings
from steering_explainer.log import get_logger

log = get_logger(__name__)


def build_paper(s: Settings) -> None:
    src = s.reports_dir / "paper" / "paper.md"
    pdf = src.with_suffix(".pdf")
    cmd = ["pandoc", str(src), "-o", str(pdf), "--pdf-engine=xelatex", "--resource-path", str(s.reports_dir),
           "-V", "mainfont=Cambria", "-V", "mathfont=Cambria Math", "-V", "geometry:margin=2.2cm",
           "-V", "colorlinks=true", "--number-sections"]
    log.info("$ %s", " ".join(cmd))
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    for line in (out.stdout + out.stderr).splitlines():
        if line.strip() and "major issue" not in line:  # MiKTeX's "check for updates" nag is noise
            log.info("  %s", line)
    if out.returncode != 0:
        raise RuntimeError(f"pandoc failed ({out.returncode})")
    log.info("Paper written to %s", pdf)
