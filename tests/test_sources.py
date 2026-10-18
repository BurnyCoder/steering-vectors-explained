"""test_sources.py — every on-screen quote must exist verbatim in its cited source.

Global context: data/sources.yaml is the single source of truth for citations and quotes; the
`network` test downloads each source once (cached under data/cache/) and checks every quote.
"""

import pytest  # markers + fixtures

from steering_explainer import sources  # module under test
from steering_explainer.config import ROOT  # repo root to find data/sources.yaml


def test_normalize_unifies_quotes_dashes_and_whitespace():
    raw = "“Love”  versus\n“Hate” – it’s −1"  # curly quotes, en dash, U+2212 minus, newline
    assert sources.normalize(raw) == "\"Love\" versus \"Hate\" - it's -1"


def test_html_to_text_and_quote_matching():
    text = sources.html_to_text("<p>We call these <b>vectors</b>\n steering vectors.</p>")
    assert sources.contains_quote(text, "We call these vectors steering vectors.")


def test_registry_schema_and_license_rule():
    reg = sources.load_sources(ROOT / "data" / "sources.yaml")
    assert reg, "sources.yaml must not be empty"
    seen = set()  # quote ids must be globally unique so scenes can reference them
    for src in reg.values():
        assert src.url.startswith("http") and src.citation and src.license and src.short
        for q in src.quotes:
            assert q.id not in seen
            seen.add(q.id)
            if src.license != "CC BY 4.0":  # non-CC-BY text: short quotes only
                assert len(q.text.split()) <= 15, f"{q.id} is too long for license {src.license}"


@pytest.mark.network
def test_every_quote_is_verbatim_in_its_source():
    reg = sources.load_sources(ROOT / "data" / "sources.yaml")
    missing = sources.verify_quotes(reg, ROOT / "data" / "cache" / "sources")
    assert missing == [], f"quotes not found verbatim: {missing}"
