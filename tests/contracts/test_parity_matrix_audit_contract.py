"""Independent contract tests for src/gates/parity_matrix.py.

Derived from observation of the audit output's behavior, NOT by reading
existing tests/parity/ tests. The contract here is: every claimed Unity
API in src/reference/mappings/ that is actually implemented in src/engine/
should be marked has_python_impl=True. The validator agent observed the
audit produced systematic false-negatives for classes whose mapping rows
do not appear in classes.json (Component, Time, Input, Object) — these
contracts will fail on the current audit code.

If these contracts fail, the audit's 72.6% impl rate is an UNDER-COUNT,
not a real measurement.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.gates.parity_matrix import build_matrix

ROOT = Path(__file__).resolve().parent.parent.parent
MAPPINGS_DIR = ROOT / "src" / "reference" / "mappings"
PARITY_TESTS_DIR = ROOT / "tests" / "parity"


@pytest.fixture(scope="module")
def matrix() -> dict:
    return build_matrix(MAPPINGS_DIR, PARITY_TESTS_DIR)


def _row(matrix: dict, unity_class: str, member: str, kind: str) -> dict:
    for row in matrix["rows"]:
        if (
            row["unity_class"] == unity_class
            and row["unity_member"] == member
            and row["kind"] == kind
        ):
            return row
    pytest.fail(f"No row for {unity_class}.{member} ({kind})")


# --- Section 1: Real implementations exist in src/engine/ ---


def test_engine_actually_has_component_attributes() -> None:
    """Sanity: Component class in src.engine.core defines gameObject/transform/enabled.

    If this fails, the engine itself is broken, not the audit.
    """
    from src.engine.core import Component

    assert hasattr(Component, "game_object")
    assert hasattr(Component, "transform")
    assert hasattr(Component, "enabled")


def test_engine_actually_has_time_properties() -> None:
    """Time class in src.engine.time_manager defines deltaTime, time, etc."""
    from src.engine.time_manager import Time

    assert hasattr(Time, "delta_time")
    assert hasattr(Time, "fixed_delta_time")
    assert hasattr(Time, "time")
    assert hasattr(Time, "frame_count")
    assert hasattr(Time, "time_scale")


def test_engine_actually_has_input_methods() -> None:
    """Input class in src.engine.input_manager defines GetKey, GetAxis, etc."""
    from src.engine.input_manager import Input

    assert hasattr(Input, "get_key")
    assert hasattr(Input, "get_key_down")
    assert hasattr(Input, "get_axis")


def test_engine_has_destroy_on_gameobject() -> None:
    """Object.Destroy maps to GameObject.destroy in src.engine.core."""
    from src.engine.core import GameObject

    assert hasattr(GameObject, "destroy")


# --- Section 2: Audit must not under-count those implementations ---


def test_audit_marks_component_properties_implemented(matrix: dict) -> None:
    """BUG: Component is not in classes.json so class_module_index lookup fails.

    Component.gameObject/transform/enabled all exist in src/engine/core.py
    and should be marked has_python_impl=True.
    """
    for prop in ("gameObject", "transform", "enabled"):
        row = _row(matrix, "Component", prop, "property")
        assert row["has_python_impl"], (
            f"Component.{prop} exists in src.engine.core but audit reports "
            f"has_python_impl=False (likely because Component lacks a "
            f"classes.json row, so class_module_index has no entry)."
        )


def test_audit_marks_time_properties_implemented(matrix: dict) -> None:
    """BUG: Time is not in classes.json. Time properties all flip to False."""
    for prop in ("deltaTime", "fixedDeltaTime", "time", "frameCount", "timeScale"):
        row = _row(matrix, "Time", prop, "property")
        assert row["has_python_impl"], (
            f"Time.{prop} exists in src.engine.time_manager but audit reports "
            f"has_python_impl=False."
        )


def test_audit_marks_input_methods_implemented(matrix: dict) -> None:
    """BUG: Input is not in classes.json. Input methods all flip to False."""
    for method in ("GetKey", "GetKeyDown", "GetAxis"):
        row = _row(matrix, "Input", method, "method")
        assert row["has_python_impl"], (
            f"Input.{method} exists in src.engine.input_manager but audit "
            f"reports has_python_impl=False."
        )


def test_audit_marks_object_destroy_implemented(matrix: dict) -> None:
    """BUG: methods.json says python_class=GameObject for Object.Destroy.

    The audit's class_module_index lookup uses unity_class ('Object'), not
    python_class ('GameObject'), so the lookup misses.
    """
    row = _row(matrix, "Object", "Destroy", "method")
    assert row["has_python_impl"], (
        "Object.Destroy → GameObject.destroy exists but audit reports "
        "has_python_impl=False (lookup uses unity_class instead of python_class)."
    )


def test_audit_marks_gameobject_layer_and_activeself_implemented(matrix: dict) -> None:
    """GameObject.layer is set in __init__; GameObject.activeSelf maps to .active.

    The audit uses snake-case-of-camelCase: activeSelf -> active_self,
    which doesn't exist; the engine just exposes .active. This is a
    convention-mismatch bug — properties.json claims python_property=active
    but the audit doesn't read python_property.
    """
    row_layer = _row(matrix, "GameObject", "layer", "property")
    row_active = _row(matrix, "GameObject", "activeSelf", "property")
    # layer is an instance attribute; class-level hasattr(GameObject, 'layer')
    # is False, so the audit (which checks hasattr on the class) misses it.
    # We assert what *should* happen: properties that the engine provides
    # (even instance-level) should be marked implemented.
    from src.engine.core import GameObject

    g = GameObject("x")
    assert hasattr(g, "layer"), "engine instance should have layer"
    assert hasattr(g, "active"), "engine instance should have active (Unity activeSelf)"

    assert row_layer["has_python_impl"], (
        "GameObject.layer exists on instances but audit reports False "
        "(audit only checks class-level hasattr)."
    )
    # activeSelf -> active mapping needs python_property awareness:
    assert row_active["has_python_impl"], (
        "GameObject.activeSelf maps to .active per properties.json but audit "
        "reports False (audit ignores python_property override and uses "
        "snake-case derivation 'active_self')."
    )


# --- Section 3: Aggregate sanity ---


def test_totals_consistency(matrix: dict) -> None:
    """Sum of by_kind totals equals total_apis equals len(rows)."""
    assert matrix["total_apis"] == len(matrix["rows"])
    by_kind_total = sum(b["total"] for b in matrix["by_kind"].values())
    assert by_kind_total == matrix["total_apis"]
    by_kind_impl = sum(b["implemented"] for b in matrix["by_kind"].values())
    assert by_kind_impl == matrix["implemented"]


def test_by_unity_class_consistency(matrix: dict) -> None:
    """Sum of by_unity_class totals equals total_apis."""
    by_class_total = sum(b["total"] for b in matrix["by_unity_class"].values())
    assert by_class_total == matrix["total_apis"]


def test_implementation_pct_within_range(matrix: dict) -> None:
    """impl_pct must be in [0, 1] and equal implemented/total."""
    pct = matrix["implementation_pct"]
    assert 0.0 <= pct <= 1.0
    assert abs(pct - matrix["implemented"] / matrix["total_apis"]) < 0.01


def test_emitted_json_matches_built_matrix() -> None:
    """The on-disk parity_matrix.json should equal what build_matrix produces.

    If they differ, regen has drifted from the committed artifact.
    """
    on_disk = json.loads((ROOT / "data" / "metrics" / "parity_matrix.json").read_text())
    fresh = build_matrix(MAPPINGS_DIR, PARITY_TESTS_DIR)
    assert on_disk["total_apis"] == fresh["total_apis"]
    assert on_disk["implemented"] == fresh["implemented"]
    assert on_disk["with_parity_test"] == fresh["with_parity_test"]
