"""Parity test: UnityEngine.Transform.childCount (M-9 phase 1).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Transform-childCount.html):
    Transform.childCount returns the number of direct children. Read-only.
    Default for a freshly-created Transform is 0. Reparenting a child via
    SetParent updates the OLD parent's count (decremented) and the NEW
    parent's count (incremented).

Python impl: src.engine.transform.Transform.child_count (property)
              src.engine.transform.Transform.set_parent (method)
"""

from __future__ import annotations

from src.engine.core import GameObject
from tests.parity._harness import ParityCase, assert_parity


def _py_default_child_count_is_zero() -> dict:
    go = GameObject("t")
    return {"count": go.transform.child_count}


_CS_DEFAULT_CHILD_COUNT = """
var go = new GameObject("t");
observables["count"] = go.transform.childCount;
"""


def test_default_child_count_is_zero_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.childCount default = 0",
            scenario_python=_py_default_child_count_is_zero,
            scenario_csharp_body=_CS_DEFAULT_CHILD_COUNT,
        )
    )


def _py_set_parent_increments_child_count() -> dict:
    parent = GameObject("p")
    a = GameObject("a")
    b = GameObject("b")
    a.transform.set_parent(parent.transform)
    b.transform.set_parent(parent.transform)
    return {
        "parent_count": parent.transform.child_count,
        "a_count": a.transform.child_count,
        "b_count": b.transform.child_count,
    }


_CS_SET_PARENT_INCREMENTS = """
var parent = new GameObject("p");
var a = new GameObject("a");
var b = new GameObject("b");
a.transform.SetParent(parent.transform);
b.transform.SetParent(parent.transform);
observables["parent_count"] = parent.transform.childCount;
observables["a_count"] = a.transform.childCount;
observables["b_count"] = b.transform.childCount;
"""


def test_set_parent_increments_count_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.childCount tracks SetParent calls",
            scenario_python=_py_set_parent_increments_child_count,
            scenario_csharp_body=_CS_SET_PARENT_INCREMENTS,
        )
    )


def _py_reparent_decrements_old_parent() -> dict:
    p1 = GameObject("p1")
    p2 = GameObject("p2")
    child = GameObject("child")
    child.transform.set_parent(p1.transform)
    child.transform.set_parent(p2.transform)
    return {
        "p1_count": p1.transform.child_count,
        "p2_count": p2.transform.child_count,
    }


_CS_REPARENT_DECREMENTS = """
var p1 = new GameObject("p1");
var p2 = new GameObject("p2");
var child = new GameObject("child");
child.transform.SetParent(p1.transform);
child.transform.SetParent(p2.transform);
observables["p1_count"] = p1.transform.childCount;
observables["p2_count"] = p2.transform.childCount;
"""


def test_reparent_decrements_old_parent_count_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.childCount: reparent decrements old, increments new",
            scenario_python=_py_reparent_decrements_old_parent,
            scenario_csharp_body=_CS_REPARENT_DECREMENTS,
        )
    )
