"""tts_edge.py — a manim-voiceover SpeechService that speaks with Microsoft Edge neural voices.

Global context: manim-voiceover (https://voiceover.manim.community) syncs animations to narration
and caches audio. It has no edge-tts backend, so this subclass follows the structure of its
built-in GTTSService (manim_voiceover/services/gtts.py) and additionally returns word timings, which
enable `<bookmark mark="x"/>` sync (the Azure service does the same).
edge-tts API: Communicate(text, voice, rate=..., boundary="WordBoundary").stream() yields
{"type": "audio", "data": bytes} and {"type": "WordBoundary", "offset", "duration", "text"}
with offsets in 100-ns ticks (https://github.com/rany2/edge-tts/blob/master/src/edge_tts/communicate.py).
"""

import asyncio  # edge-tts is async; asyncio.run drives one synthesis
from pathlib import Path  # cache paths

import edge_tts  # client for the Edge "Read aloud" TTS endpoint
from manim_voiceover.helper import remove_bookmarks  # strips <bookmark .../> tags before speaking
from manim_voiceover.services.base import SpeechService  # abstract base: implement generate_from_text

from steering_explainer.log import get_logger  # timestamped run log

log = get_logger(__name__)


def edge_to_word_boundaries(chunks: list[dict], text: str) -> list[dict]:
    """Convert edge-tts WordBoundary chunks into manim-voiceover `word_boundaries` entries.

    `text_offset` must index `text` (the bookmark-free narration) because the tracker interpolates
    bookmark times over character positions (manim_voiceover/tracker.py::_process_bookmarks).
    """
    out, cursor = [], 0  # cursor = where the search for the next spoken word starts
    for ch in chunks:
        if ch.get("type") != "WordBoundary":  # ignore audio / sentence chunks
            continue
        pos = text.find(ch["text"], cursor)  # locate the spoken word in the written text
        if pos < 0:  # TTS normalised it (e.g. "0" -> "zero"): skip rather than misalign
            continue
        out.append({"audio_offset": int(ch["offset"]),  # ticks (1e-7 s), same unit as Azure
                    "duration_milliseconds": int(ch["duration"]) // 10_000,  # ticks -> ms
                    "text_offset": pos, "word_length": len(ch["text"]),
                    "text": ch["text"], "boundary_type": "Word"})
        cursor = pos + len(ch["text"])  # continue after this word so repeats map in order
    return out


async def _synthesize(text: str, voice: str, rate: str, mp3_path: Path) -> list[dict]:
    """Stream audio to `mp3_path` and collect word-boundary metadata."""
    comm = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")  # word timings on
    chunks = []  # metadata chunks
    with open(mp3_path, "wb") as f:
        async for ch in comm.stream():  # interleaved audio bytes + boundary events
            if ch["type"] == "audio":
                f.write(ch["data"])  # append MP3 frames
            else:
                chunks.append(ch)  # keep WordBoundary events
    return chunks


class EdgeTTSService(SpeechService):
    """manim-voiceover speech service backed by edge-tts (online, free neural voices)."""

    def __init__(self, voice: str = "en-US-AndrewMultilingualNeural", rate: str = "+0%", **kwargs):
        self.voice, self.rate = voice, rate  # stored before base init (base may log/inspect)
        SpeechService.__init__(self, **kwargs)  # sets cache_dir, global_speed, transcription=None

    def generate_from_text(self, text: str, cache_dir=None, path=None, **kwargs) -> dict:
        """Synthesise `text` (cached by voice+rate+text), returning manim-voiceover's data dict."""
        cache_dir = Path(cache_dir or self.cache_dir)  # default: media/voiceovers
        input_text = remove_bookmarks(text)  # bookmarks are timing marks, never spoken
        input_data = {"input_text": input_text, "service": "edge_tts", "voice": self.voice, "rate": self.rate}
        cached = self.get_cached_result(input_data, cache_dir)  # cache hit -> no network call
        if cached is not None:
            return cached
        audio_name = str(path) if path else self.get_audio_basename(input_data) + ".mp3"  # slug-hash.mp3
        log.info("TTS synthesize [%s %s]: %s", self.voice, self.rate, input_text)  # full narration logged
        chunks = asyncio.run(_synthesize(input_text, self.voice, self.rate, cache_dir / audio_name))
        return {"input_text": text, "input_data": input_data, "original_audio": audio_name,
                "word_boundaries": edge_to_word_boundaries(chunks, input_text)}
