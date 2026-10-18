"""test_tts_edge.py — edge-tts word timings must map onto manim-voiceover's bookmark format.

Global context: manim-voiceover interpolates bookmark times from `word_boundaries` whose
`text_offset` indexes the bookmark-free text and whose `audio_offset` is in 100-ns ticks
(manim_voiceover/tracker.py, AUDIO_OFFSET_RESOLUTION = 10_000_000). edge-tts emits the same tick unit.
"""

from steering_explainer.video.tts_edge import edge_to_word_boundaries  # pure function under test


def test_offsets_follow_text_positions():
    text = "A vector, like two one."  # punctuation is skipped by the TTS boundaries
    chunks = [  # shape of edge_tts.Communicate(..., boundary="WordBoundary").stream() metadata
        {"type": "WordBoundary", "offset": 875000, "duration": 500000, "text": "A"},
        {"type": "WordBoundary", "offset": 1500000, "duration": 5625000, "text": "vector"},
        {"type": "WordBoundary", "offset": 9000000, "duration": 2000000, "text": "like"},
        {"type": "WordBoundary", "offset": 12000000, "duration": 1000000, "text": "two"},
        {"type": "WordBoundary", "offset": 14000000, "duration": 1000000, "text": "one"},
    ]
    wbs = edge_to_word_boundaries(chunks, text)
    assert [w["text_offset"] for w in wbs] == [0, 2, 10, 15, 19]  # character index of each word
    assert wbs[1]["audio_offset"] == 1500000  # ticks passed through unchanged
    assert wbs[1]["duration_milliseconds"] == 562  # 5_625_000 ticks = 562.5 ms (floored)
    assert all(w["boundary_type"] == "Word" for w in wbs)


def test_unmatched_word_is_skipped_not_misaligned():
    chunks = [{"type": "WordBoundary", "offset": 0, "duration": 1, "text": "zero"},
              {"type": "WordBoundary", "offset": 5, "duration": 1, "text": "one"}]
    wbs = edge_to_word_boundaries(chunks, "0 one")  # TTS normalised "0" to "zero"
    assert [w["text"] for w in wbs] == ["one"] and wbs[0]["text_offset"] == 2
