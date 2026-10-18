"""sources.py — citation registry + automatic verbatim-quote verification.

Global context: data/sources.yaml lists every source (citation, URL, license) and every quote
shown on screen. `verify_quotes` downloads each source once (cached in data/cache/sources), turns
HTML/PDF into plain text and checks that each quote occurs verbatim after whitespace/typography
normalisation — a guard against hallucinated or drifted quotations.
Docs: BeautifulSoup get_text (https://www.crummy.com/software/BeautifulSoup/bs4/doc/#get-text),
pypdf text extraction (https://pypdf.readthedocs.io/en/stable/user/extract-text.html).
"""

import io  # wrap downloaded PDF bytes as a file object for pypdf
import re  # whitespace collapsing
import unicodedata  # NFKC folds ligatures/compatibility characters (e.g. "ﬁ" -> "fi")
from dataclasses import dataclass, field  # immutable records
from pathlib import Path  # cache paths

import requests  # HTTP downloads
import yaml  # parse data/sources.yaml
from bs4 import BeautifulSoup  # HTML -> text
from pypdf import PdfReader  # PDF -> text

from steering_explainer.log import get_logger

log = get_logger(__name__)

# Typographic variants mapped to ASCII so “Love” in a PDF matches "Love" in YAML.
_TRANSLATE = str.maketrans({"“": '"', "”": '"', "„": '"', "‘": "'", "’": "'", "–": "-", "—": "-",
                            "−": "-", " ": " ", " ": " ", " ": " "})


@dataclass(frozen=True)
class Quote:
    """One verbatim excerpt; `id` is how scenes refer to it."""
    id: str
    text: str
    location: str  # section / page in the source


@dataclass(frozen=True)
class Source:
    """One cited work."""
    id: str
    short: str  # on-screen footer label, e.g. "Turner et al. 2024, arXiv:2308.10248"
    citation: str  # full reference for README/paper
    url: str  # human-facing link
    license: str  # governs quote length (non-"CC BY 4.0" -> at most 15 words)
    fetch_url: str = ""  # machine-readable text used for verification (HTML or PDF)
    quotes: tuple[Quote, ...] = field(default_factory=tuple)


def load_sources(path: Path) -> dict[str, Source]:
    """Parse sources.yaml into {source_id: Source}."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))  # list of source mappings
    reg = {}
    for s in raw["sources"]:
        quotes = tuple(Quote(**q) for q in s.pop("quotes", []))  # nested quote records
        reg[s["id"]] = Source(quotes=quotes, **s)
    return reg


def normalize(text: str) -> str:
    """NFKC + ASCII quotes/dashes + single spaces: makes HTML, PDF and YAML text comparable."""
    text = unicodedata.normalize("NFKC", text).translate(_TRANSLATE)  # fold typography
    return re.sub(r"\s+", " ", text).strip()  # collapse newlines/tabs/multiple spaces


def html_to_text(html: str) -> str:
    """Visible text of an HTML page with tags replaced by spaces."""
    soup = BeautifulSoup(html, "html.parser")  # stdlib parser: no lxml dependency
    for tag in soup(["script", "style"]):  # drop non-visible code
        tag.decompose()
    return soup.get_text(" ")  # separator " " keeps words from gluing across tags


def pdf_to_text(data: bytes) -> str:
    """Concatenated text layer of every PDF page."""
    return " ".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(data)).pages)


def contains_quote(source_text: str, quote: str) -> bool:
    """True if `quote` appears in `source_text` after normalisation (also tolerant to hyphenation spaces)."""
    hay, needle = normalize(source_text), normalize(quote)
    if needle in hay:
        return True
    squash = lambda s: re.sub(r"\s+", "", s)  # PDF line breaks can split words: compare without spaces
    return squash(needle) in squash(hay)


def fetch_text(src: Source, cache_dir: Path) -> str:
    """Download (once) and return the plain text of a source."""
    url = src.fetch_url or src.url
    cache_dir.mkdir(parents=True, exist_ok=True)
    is_pdf = url.lower().endswith(".pdf")
    cache = cache_dir / f"{src.id}.{'pdf' if is_pdf else 'html'}"  # one raw file per source
    if not cache.exists():
        log.info("Downloading source %s from %s", src.id, url)
        r = requests.get(url, timeout=60, headers={"User-Agent": "steering-explainer/0.1 (quote verification)"})
        r.raise_for_status()  # fail loudly on 404 etc.
        cache.write_bytes(r.content)
    data = cache.read_bytes()
    return pdf_to_text(data) if is_pdf else html_to_text(data.decode("utf-8", errors="replace"))


def verify_quotes(reg: dict[str, Source], cache_dir: Path) -> list[str]:
    """Return ids of quotes NOT found verbatim in their source (empty list = all verified)."""
    missing = []
    for src in reg.values():
        if not src.quotes:  # sources cited without quotation need no download
            continue
        text = fetch_text(src, cache_dir)
        for q in src.quotes:
            ok = contains_quote(text, q.text)
            log.info("Quote %-28s %s", q.id, "VERIFIED" if ok else "NOT FOUND")
            if not ok:
                missing.append(q.id)
    return missing


def get_quote(reg: dict[str, Source], quote_id: str) -> tuple[Quote, Source]:
    """Look up a quote and its source by quote id (used by the video's QuoteCard)."""
    for src in reg.values():
        for q in src.quotes:
            if q.id == quote_id:
                return q, src
    raise KeyError(quote_id)
