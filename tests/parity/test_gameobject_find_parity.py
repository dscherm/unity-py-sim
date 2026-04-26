"""Parity tests: UnityEngine.GameObject.Find and FindWithTag.

Documented Unity behavior:
- https://docs.unity3d.com/ScriptReference/GameObject.Find.html
- https://docs.unity3d.com/ScriptReference/GameObject.FindWithTag.html

Find(name): returns the active GameObject whose name matches, or null
(None in Python) if no match. Inactive GameObjects are not searched.
FindWithTag(tag): same semantics keyed by tag instead of name.
Both are static; both return null/None on no-match (do NOT throw).
"""

from __future__ import annotations

import pytest

from src.engine.core import GameObject


@pytest.fixture(autouse=True)
def _isolate_registry():
    """Tear down any GameObject registry state between tests."""
    yield
    # Engine-internal: registry usually lives on GameObject as a class attr.
    # If a clear() helper exists, use it; otherwise manually reset known fields.
    for attr in ("_registry", "_instances", "_all"):
        reg = getattr(GameObject, attr, None)
        if hasattr(reg, "clear"):
            try:
                reg.clear()
            except Exception:
                pass


def test_find_returns_named_gameobject():
    GameObject("ParityFinder")
    found = GameObject.find("ParityFinder")
    assert found is not None, "Find must locate an active GameObject by name"
    assert found.name == "ParityFinder"


def test_find_returns_none_for_missing_name():
    """Unity's GameObject.Find returns null for unknown names — never throws."""
    result = GameObject.find("DefinitelyNotInScene_xyz_123")
    assert result is None, f"expected None, got {result!r}"


def test_find_with_tag_returns_tagged_gameobject():
    go = GameObject("Tagged")
    go.tag = "Player"
    found = GameObject.find_with_tag("Player")
    assert found is not None
    assert found.name == "Tagged"


def test_find_with_tag_returns_none_for_missing_tag():
    """Like Find, FindWithTag returns null for unmatched tags rather
    than throwing."""
    result = GameObject.find_with_tag("NoSuchTagInScene")
    assert result is None


def test_find_is_static():
    """Find is a @staticmethod — callable from the class without an
    instance. Documented as `static GameObject Find(string)`."""
    # If find required `self`, this would TypeError.
    GameObject("staticness_check")
    result = GameObject.find("staticness_check")
    assert result is not None
