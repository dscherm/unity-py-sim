"""Parity test: UnityEngine.Camera.orthographicSize (M-9 phase 4).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Camera-orthographicSize.html):
    Camera.orthographicSize is a float — half the height of the orthographic view
    in world units. Default 5.0. Writeable. Only meaningful when Camera.orthographic = true.

Python impl: src.engine.rendering.camera.Camera.orthographic_size (property)
"""

from __future__ import annotations

from src.engine.rendering.camera import Camera
from tests.parity._harness import ParityCase, assert_parity


def _py_default_orthographic_size() -> dict:
    cam = Camera()
    return {"orthographic_size": cam.orthographic_size}


_CS_DEFAULT_ORTHOGRAPHIC_SIZE = """
var cam = new Camera();
observables["orthographic_size"] = cam.orthographicSize;
"""


def test_default_orthographic_size_is_5_parity() -> None:
    assert_parity(
        ParityCase(
            name="Camera.orthographicSize default = 5.0",
            scenario_python=_py_default_orthographic_size,
            scenario_csharp_body=_CS_DEFAULT_ORTHOGRAPHIC_SIZE,
        )
    )


def _py_orthographic_size_round_trip() -> dict:
    cam = Camera()
    cam.orthographic_size = 10.0
    return {"orthographic_size": cam.orthographic_size}


_CS_ORTHOGRAPHIC_SIZE_ROUND_TRIP = """
var cam = new Camera();
cam.orthographicSize = 10.0f;
observables["orthographic_size"] = cam.orthographicSize;
"""


def test_orthographic_size_setter_round_trip_parity() -> None:
    assert_parity(
        ParityCase(
            name="Camera.orthographicSize setter round-trip",
            scenario_python=_py_orthographic_size_round_trip,
            scenario_csharp_body=_CS_ORTHOGRAPHIC_SIZE_ROUND_TRIP,
        )
    )
