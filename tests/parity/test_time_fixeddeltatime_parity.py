"""Parity test: UnityEngine.Time.fixedDeltaTime (M-9 phase 3).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Time-fixedDeltaTime.html):
    Time.fixedDeltaTime is a static float, the interval (seconds) between
    FixedUpdate calls. Unity's default is 0.02 (50 Hz physics). Settable, but
    typically left at default.

Python impl: src.engine.time_manager.Time.fixed_delta_time (descriptor)
"""

from __future__ import annotations

from src.engine.time_manager import Time
from tests.parity._harness import ParityCase, assert_parity


def _py_default_fixed_delta_time() -> dict:
    return {"fixed_delta_time": float(Time.fixed_delta_time)}


_CS_DEFAULT_FIXED_DELTA_TIME = """
observables["fixed_delta_time"] = Time.fixedDeltaTime;
"""


def test_default_fixed_delta_time_is_50hz_parity() -> None:
    assert_parity(
        ParityCase(
            name="Time.fixedDeltaTime default = 0.02 (50 Hz)",
            scenario_python=_py_default_fixed_delta_time,
            scenario_csharp_body=_CS_DEFAULT_FIXED_DELTA_TIME,
        )
    )
