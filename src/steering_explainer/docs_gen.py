"""docs_gen.py — generate docs/glossary.md and docs/sources.md from the YAML single sources of truth.

Global context: definitions live once in data/glossary.yaml and citations/quotes once in
data/sources.yaml; this phase renders them to Markdown so README/docs never duplicate (or drift from)
the data the video and tests use.
"""

import yaml

from steering_explainer import sources
from steering_explainer.config import Settings


def write_docs(s: Settings) -> None:
    docs = s.root / "docs"
    docs.mkdir(exist_ok=True)
    terms = yaml.safe_load((s.data_dir / "glossary.yaml").read_text(encoding="utf-8"))["terms"]
    lines = ["# Glossary (generated from data/glossary.yaml)", "",
             "Every term in the order the video defines it. `chapter` = first chapter whose narration defines it",
             "(enforced by tests/test_script.py).", "", "| Term | Chapter | Definition |", "|---|---|---|"]
    lines += [f"| {t['term']} | {t['chapter']} | {t['definition']} |" for t in terms]
    (docs / "glossary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    reg = sources.load_sources(s.data_dir / "sources.yaml")
    out = ["# Sources and verbatim quotes (generated from data/sources.yaml)", "",
           "Every quote below is checked verbatim against the downloaded source by `verify_sources`",
           "(and `uv run pytest -m network`). Quotes from non-CC-BY-4.0 sources are kept to at most 15 words.", ""]
    for src in reg.values():
        out += [f"## {src.short}", "", f"{src.citation}  ", f"Link: {src.url}  ", f"License: {src.license}", ""]
        out += [f"- **{q.id}** ({q.location}): “{q.text}”" for q in src.quotes]
        out += [""]
    (docs / "sources.md").write_text("\n".join(out), encoding="utf-8")
