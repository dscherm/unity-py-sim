"""Parity test: UnityEngine.Input.GetKey (M-9 phase 3).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Input.GetKey.html):
    Input.GetKey(string name) returns true while the named key is held down.
    Returns false when no input devices are bound (batchmode / no keyboard).

Python impl: src.engine.input_manager.Input.get_key (static method)
"""

from __future__ import annotations

from src.engine.input_manager import Input
from tests.parity._harness import ParityCase, assert_parity


def _py_get_key_returns_false_with_no_input() -> dict:
    return {
        "space": Input.get_key("space"),
        "a": Input.get_key("a"),
        "missing": Input.get_key("not_a_real_key"),
    }


_CS_GET_KEY_NO_INPUT = """
observables["space"] = Input.GetKey("space");
observables["a"] = Input.GetKey("a");
observables["missing"] = Input.GetKey("not_a_real_key");
"""


def test_get_key_returns_false_with_no_input_parity() -> None:
    assert_parity(
        ParityCase(
            name="Input.GetKey returns false when no keyboard is bound",
            scenario_python=_py_get_key_returns_false_with_no_input,
            scenario_csharp_body=_CS_GET_KEY_NO_INPUT,
        )
    )
