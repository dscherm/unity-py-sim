"""Parity test: UnityEngine.GameObject.FindGameObjectsWithTag (M-9 phase 4).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/GameObject.FindGameObjectsWithTag.html):
    GameObject.FindGameObjectsWithTag(tag) returns an array of all GameObjects
    matching the tag. Returns an EMPTY array (not null) when nothing matches.

Python impl: src.engine.core.GameObject.find_game_objects_with_tag (static method)
"""

from __future__ import annotations

from src.engine.core import GameObject
from tests.parity._harness import ParityCase, assert_parity


def _py_find_game_objects_with_tag_no_match() -> dict:
    """No GameObjects tagged 'NotARealTag' — both legs emit empty count."""
    matches = GameObject.find_game_objects_with_tag("NotARealTag")
    return {"count": len(matches)}


_CS_FIND_GAME_OBJECTS_WITH_TAG_NO_MATCH = """
var matches = GameObject.FindGameObjectsWithTag("NotARealTag");
observables["count"] = matches.Length;
"""


def test_find_game_objects_with_tag_returns_empty_when_no_match_parity() -> None:
    assert_parity(
        ParityCase(
            name="GameObject.FindGameObjectsWithTag returns empty array when no match",
            scenario_python=_py_find_game_objects_with_tag_no_match,
            scenario_csharp_body=_CS_FIND_GAME_OBJECTS_WITH_TAG_NO_MATCH,
        )
    )
