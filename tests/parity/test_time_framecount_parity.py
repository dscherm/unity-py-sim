"""Parity test: UnityEngine.Time.frameCount (M-9 phase 3).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Time-frameCount.html):
    Time.frameCount is a static int — total frames rendered. Read-only.
    Default 0 before the loop has ticked.

Python impl: src.engine.time_manager.Time.frame_count (descriptor)
"""

from __future__ import annotations

from src.engine.time_manager import Time
from tests.parity._harness import ParityCase, assert_parity


def _py_default_frame_count() -> dict:
    return {"frame_count": int(Time.frame_count)}


_CS_DEFAULT_FRAME_COUNT = """
observables["frame_count"] = Time.frameCount;
"""


def test_default_frame_count_is_zero_parity() -> None:
    assert_parity(
        ParityCase(
            name="Time.frameCount default = 0",
            scenario_python=_py_default_frame_count,
            scenario_csharp_body=_CS_DEFAULT_FRAME_COUNT,
        )
    )
