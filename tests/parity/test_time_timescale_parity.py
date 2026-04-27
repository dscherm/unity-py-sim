"""Parity test: UnityEngine.Time.timeScale (M-9 phase 3).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Time-timeScale.html):
    Time.timeScale is a static float multiplier on the simulation rate. Default
    1.0 (real time). Setting to 0 pauses simulation. Setting via Time.timeScale
    in C# / Time.set_time_scale in Python.

Python impl: src.engine.time_manager.Time.time_scale (descriptor)
"""

from __future__ import annotations

import pytest

from src.engine.time_manager import Time
from tests.parity._harness import ParityCase, assert_parity


@pytest.fixture(autouse=True)
def reset_time_scale():
    """Time is a singleton; restore default after each test."""
    yield
    Time._time_scale = 1.0


def _py_default_time_scale() -> dict:
    return {"time_scale": float(Time.time_scale)}


_CS_DEFAULT_TIME_SCALE = """
observables["time_scale"] = Time.timeScale;
"""


def test_default_time_scale_is_one_parity() -> None:
    assert_parity(
        ParityCase(
            name="Time.timeScale default = 1.0",
            scenario_python=_py_default_time_scale,
            scenario_csharp_body=_CS_DEFAULT_TIME_SCALE,
        )
    )


def _py_time_scale_zero_pauses() -> dict:
    Time.set_time_scale(0.0)
    return {"time_scale": float(Time.time_scale)}


_CS_TIME_SCALE_ZERO = """
Time.timeScale = 0.0f;
observables["time_scale"] = Time.timeScale;
"""


def test_time_scale_zero_round_trip_parity() -> None:
    assert_parity(
        ParityCase(
            name="Time.timeScale = 0 round-trip (paused)",
            scenario_python=_py_time_scale_zero_pauses,
            scenario_csharp_body=_CS_TIME_SCALE_ZERO,
        )
    )
