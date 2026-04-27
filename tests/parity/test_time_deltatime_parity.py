"""Parity test: UnityEngine.Time.deltaTime (M-9 phase 3).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Time-deltaTime.html):
    Time.deltaTime is a static float of seconds since the last frame.
    Default 0 before the loop has ticked. Read-only at the API surface; the
    game-loop owns the writes.

Python impl: src.engine.time_manager.Time.delta_time (descriptor)
"""

from __future__ import annotations

from src.engine.time_manager import Time
from tests.parity._harness import ParityCase, assert_parity


def _py_default_delta_time() -> dict:
    return {"delta_time": float(Time.delta_time)}


_CS_DEFAULT_DELTA_TIME = """
observables["delta_time"] = Time.deltaTime;
"""


def test_default_delta_time_is_zero_parity() -> None:
    assert_parity(
        ParityCase(
            name="Time.deltaTime default = 0 (no game-loop tick)",
            scenario_python=_py_default_delta_time,
            scenario_csharp_body=_CS_DEFAULT_DELTA_TIME,
        )
    )
