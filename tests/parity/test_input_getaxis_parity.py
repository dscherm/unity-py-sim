"""Parity test: UnityEngine.Input.GetAxis (M-9 phase 3).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Input.GetAxis.html):
    Input.GetAxis(string name) returns the axis value in [-1.0, 1.0]. Common axes:
    "Horizontal", "Vertical". Returns 0.0 when no input is bound.

Python impl: src.engine.input_manager.Input.get_axis (static method)
"""

from __future__ import annotations

from src.engine.input_manager import Input
from tests.parity._harness import ParityCase, assert_parity


def _py_get_axis_returns_zero_with_no_input() -> dict:
    return {
        "horizontal": Input.get_axis("Horizontal"),
        "vertical": Input.get_axis("Vertical"),
        "unknown": Input.get_axis("not_a_real_axis"),
    }


_CS_GET_AXIS_NO_INPUT = """
observables["horizontal"] = Input.GetAxis("Horizontal");
observables["vertical"] = Input.GetAxis("Vertical");
observables["unknown"] = Input.GetAxis("not_a_real_axis");
"""


def test_get_axis_returns_zero_with_no_input_parity() -> None:
    assert_parity(
        ParityCase(
            name="Input.GetAxis returns 0 when no input is bound",
            scenario_python=_py_get_axis_returns_zero_with_no_input,
            scenario_csharp_body=_CS_GET_AXIS_NO_INPUT,
        )
    )
