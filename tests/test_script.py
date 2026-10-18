"""test_script.py — "never mention a word before defining it", checked mechanically.

Global context: data/glossary.yaml maps each term to the chapter whose narration defines it; this test
scans data/script.yaml and fails if a term appears in any earlier chapter. It also checks that every
`self.say("beat")` call in the scenes refers to an existing beat and that every beat is spoken.
"""

import re

import yaml

from steering_explainer.config import ROOT

SCRIPT = yaml.safe_load((ROOT / "data" / "script.yaml").read_text(encoding="utf-8"))["chapters"]
GLOSSARY = yaml.safe_load((ROOT / "data" / "glossary.yaml").read_text(encoding="utf-8"))["terms"]
ORDER = [c["id"] for c in SCRIPT]


def _text(chapter: dict) -> str:
    return " ".join(b["text"] for b in chapter["beats"])


def test_no_term_before_its_defining_chapter():
    problems = []
    for term in GLOSSARY:
        k = ORDER.index(term["chapter"])
        for chapter in SCRIPT[:k]:
            for alias in term["aliases"]:
                if re.search(rf"\b{re.escape(alias)}\b", _text(chapter), flags=re.IGNORECASE):
                    problems.append(f"'{alias}' used in {chapter['id']} but defined in {term['chapter']}")
    assert not problems, "\n".join(problems)


def test_each_term_is_used_in_its_defining_chapter():
    for term in GLOSSARY:
        text = _text(SCRIPT[ORDER.index(term["chapter"])])
        assert any(re.search(rf"\b{re.escape(a)}\b", text, re.IGNORECASE) for a in term["aliases"]), term["term"]


def test_scenes_speak_exactly_the_scripted_beats():
    scene_dir = ROOT / "src" / "steering_explainer" / "video" / "scenes"
    for chapter in SCRIPT:
        files = list(scene_dir.glob(f"{chapter['id']}_*.py"))
        assert len(files) == 1, f"one scene file per chapter expected for {chapter['id']}"
        spoken = re.findall(r"self\.say\(\"(\w+)\"\)", files[0].read_text(encoding="utf-8"))
        assert spoken == [b["id"] for b in chapter["beats"]], f"{chapter['id']}: beats out of sync"
