"""Parity test: UnityEngine.Input.GetKeyDown (M-9 phase 3).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Input.GetKeyDown.html):
    Input.GetKeyDown(string name) returns true ONLY on the frame the key was
    pressed (one-shot). Returns false when no input devices are bound.

Python impl: src.engine.input_manager.Input.get_key_down (static method)
"""

from __future__ import annotations

from src.engine.input_manager import Input
from tests.parity._harness import ParityCase, assert_parity


def _py_get_key_down_returns_false_with_no_input() -> dict:
    return {
        "space": Input.get_key_down("space"),
        "a": Input.get_key_down("a"),
    }


_CS_GET_KEY_DOWN_NO_INPUT = """
observables["space"] = Input.GetKeyDown("space");
observables["a"] = Input.GetKeyDown("a");
"""


def test_get_key_down_returns_false_with_no_input_parity() -> None:
    assert_parity(
        ParityCase(
            name="Input.GetKeyDown returns false when no keyboard is bound",
            scenario_python=_py_get_key_down_returns_false_with_no_input,
            scenario_csharp_body=_CS_GET_KEY_DOWN_NO_INPUT,
        )
    )
