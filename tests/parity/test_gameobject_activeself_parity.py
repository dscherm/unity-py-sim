"""Parity test: UnityEngine.GameObject.activeSelf (M-9 phase 4).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/GameObject-activeSelf.html):
    GameObject.activeSelf is a bool indicating the local active state of the
    GameObject (independent of hierarchy). Default true on construction.
    Mutated via GameObject.SetActive(value).

Python impl: src.engine.core.GameObject.active (bool attribute) +
             src.engine.core.GameObject.set_active (method)
"""

from __future__ import annotations

from src.engine.core import GameObject
from tests.parity._harness import ParityCase, assert_parity


def _py_default_active_self() -> dict:
    go = GameObject("t")
    return {"active": go.active}


_CS_DEFAULT_ACTIVE_SELF = """
var go = new GameObject("t");
observables["active"] = go.activeSelf;
"""


def test_default_active_self_is_true_parity() -> None:
    assert_parity(
        ParityCase(
            name="GameObject.activeSelf default = true",
            scenario_python=_py_default_active_self,
            scenario_csharp_body=_CS_DEFAULT_ACTIVE_SELF,
        )
    )


def _py_set_active_false() -> dict:
    go = GameObject("t")
    go.set_active(False)
    return {"active": go.active}


_CS_SET_ACTIVE_FALSE = """
var go = new GameObject("t");
go.SetActive(false);
observables["active"] = go.activeSelf;
"""


def test_set_active_false_round_trip_parity() -> None:
    assert_parity(
        ParityCase(
            name="GameObject.SetActive(false) flips activeSelf to false",
            scenario_python=_py_set_active_false,
            scenario_csharp_body=_CS_SET_ACTIVE_FALSE,
        )
    )
