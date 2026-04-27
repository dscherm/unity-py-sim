"""Parity test: UnityEngine.SpriteRenderer.sortingOrder (M-9 phase 4).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/SpriteRenderer-sortingOrder.html):
    SpriteRenderer.sortingOrder is an int controlling render order within a
    sorting layer. Default 0. Higher values render on top. Writeable.

Python impl: src.engine.rendering.renderer.SpriteRenderer.sorting_order (int attribute)
"""

from __future__ import annotations

from src.engine.rendering.renderer import SpriteRenderer
from tests.parity._harness import ParityCase, assert_parity


def _py_default_sorting_order() -> dict:
    sr = SpriteRenderer()
    return {"sorting_order": sr.sorting_order}


_CS_DEFAULT_SORTING_ORDER = """
var sr = new SpriteRenderer();
observables["sorting_order"] = sr.sortingOrder;
"""


def test_default_sorting_order_is_zero_parity() -> None:
    assert_parity(
        ParityCase(
            name="SpriteRenderer.sortingOrder default = 0",
            scenario_python=_py_default_sorting_order,
            scenario_csharp_body=_CS_DEFAULT_SORTING_ORDER,
        )
    )


def _py_sorting_order_round_trip() -> dict:
    sr = SpriteRenderer()
    sr.sorting_order = 10
    return {"sorting_order": sr.sorting_order}


_CS_SORTING_ORDER_ROUND_TRIP = """
var sr = new SpriteRenderer();
sr.sortingOrder = 10;
observables["sorting_order"] = sr.sortingOrder;
"""


def test_sorting_order_setter_round_trip_parity() -> None:
    assert_parity(
        ParityCase(
            name="SpriteRenderer.sortingOrder setter round-trip",
            scenario_python=_py_sorting_order_round_trip,
            scenario_csharp_body=_CS_SORTING_ORDER_ROUND_TRIP,
        )
    )
