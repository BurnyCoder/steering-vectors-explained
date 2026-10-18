"""test_posthoc.py — the exploratory word counts must count words, not substrings.

Global context: v1.0 matched `hat(?:e|ing|red)` / `lov` as substrings, so "whatever", "chateau" and "glove"
were counted as hate/love (docs/fact_check.md). study/posthoc.py now uses whole-word patterns.
"""

import pytest

from steering_explainer.study.posthoc import mentions


@pytest.mark.parametrize("text", ["I hate you", "Hate.", "hated", "hates", "hating", "hatred", "hateful"])
def test_hate_forms_are_counted(text):
    assert mentions([text], "hate") == [True]


@pytest.mark.parametrize("text", ["whatever", "chateau", "that every", "a hat", "hatch"])
def test_hate_substrings_are_not_counted(text):
    assert mentions([text], "hate") == [False]


@pytest.mark.parametrize("text", ["Love", "loves", "loved", "loving", "lover", "lovers"])
def test_love_forms_are_counted(text):
    assert mentions([text], "love") == [True]


@pytest.mark.parametrize("text", ["glove", "clover", "lovely", "Lovecraft"])
def test_love_substrings_are_not_counted(text):
    assert mentions([text], "love") == [False]
