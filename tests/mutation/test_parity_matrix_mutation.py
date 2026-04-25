"""Mutation tests for src/gates/parity_matrix.py.

Strategy: mutate the world (mappings JSON, engine module name) in temp
copies and confirm the audit's has_python_impl flips appropriately.

These prove that has_python_impl is not a constant — it actually responds
to import success. If a mutation breaks the import and the audit STILL
reports True, the audit is rubber-stamping its claims.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from src.gates.parity_matrix import build_matrix

ROOT = Path(__file__).resolve().parent.parent.parent
MAPPINGS_DIR = ROOT / "src" / "reference" / "mappings"
PARITY_TESTS_DIR = ROOT / "tests" / "parity"


def _find_row(matrix: dict, unity_class: str, member: str = "") -> dict:
    for row in matrix["rows"]:
        if row["unity_class"] == unity_class and row["unity_member"] == member:
            return row
    pytest.fail(f"No row for {unity_class}.{member}")


def test_breaking_python_module_flips_class_to_not_implemented(tmp_path: Path) -> None:
    """If classes.json points at a nonexistent module, has_python_impl flips to False."""
    # Copy mappings to temp
    fake_mappings = tmp_path / "mappings"
    shutil.copytree(MAPPINGS_DIR, fake_mappings)

    classes_path = fake_mappings / "classes.json"
    classes = json.loads(classes_path.read_text())
    # Mutate: break MonoBehaviour's python_module
    for entry in classes:
        if entry.get("unity_class") == "MonoBehaviour":
            entry["python_module"] = "src.engine.NONEXISTENT_MODULE_XYZ"
    classes_path.write_text(json.dumps(classes))

    matrix = build_matrix(fake_mappings, PARITY_TESTS_DIR)
    row = _find_row(matrix, "MonoBehaviour")
    assert row["has_python_impl"] is False, (
        "Audit said MonoBehaviour is implemented even though we pointed it "
        "at a nonexistent module — _check_python_impl is not actually "
        "importing."
    )


def test_breaking_python_class_name_flips_to_not_implemented(tmp_path: Path) -> None:
    """If python_class is a nonexistent class name, has_python_impl flips to False."""
    fake_mappings = tmp_path / "mappings"
    shutil.copytree(MAPPINGS_DIR, fake_mappings)

    classes_path = fake_mappings / "classes.json"
    classes = json.loads(classes_path.read_text())
    for entry in classes:
        if entry.get("unity_class") == "Vector2":
            entry["python_class"] = "Vector2_DOES_NOT_EXIST"
    classes_path.write_text(json.dumps(classes))

    matrix = build_matrix(fake_mappings, PARITY_TESTS_DIR)
    row = _find_row(matrix, "Vector2")
    assert row["has_python_impl"] is False


def test_method_inherits_module_via_class_index(tmp_path: Path) -> None:
    """Breaking the parent class's python_module also breaks its methods.

    Methods.json doesn't carry python_module — it inherits via the class
    index. Breaking the class entry should cascade to the method rows.
    """
    fake_mappings = tmp_path / "mappings"
    shutil.copytree(MAPPINGS_DIR, fake_mappings)

    classes_path = fake_mappings / "classes.json"
    classes = json.loads(classes_path.read_text())
    for entry in classes:
        if entry.get("unity_class") == "GameObject":
            entry["python_module"] = "src.engine.NONEXISTENT_FOR_GAMEOBJECT"
    classes_path.write_text(json.dumps(classes))

    matrix = build_matrix(fake_mappings, PARITY_TESTS_DIR)
    row_class = _find_row(matrix, "GameObject")
    row_find = _find_row(matrix, "GameObject", "Find")
    assert row_class["has_python_impl"] is False
    assert row_find["has_python_impl"] is False, (
        "Method GameObject.Find should follow its parent class through the "
        "class_module_index."
    )


def test_removing_parity_test_dir_zeros_test_coverage(tmp_path: Path) -> None:
    """If parity_tests_dir doesn't exist, has_parity_test is False everywhere."""
    nonexistent = tmp_path / "no_such_dir"
    matrix = build_matrix(MAPPINGS_DIR, nonexistent)
    assert matrix["with_parity_test"] == 0
    assert all(not r["has_parity_test"] for r in matrix["rows"])


def test_isolated_parity_test_dir_zeros_when_no_tests(tmp_path: Path) -> None:
    """An empty test dir gives zero parity-test coverage even though impl coverage holds."""
    empty_dir = tmp_path / "parity_empty"
    empty_dir.mkdir()

    matrix = build_matrix(MAPPINGS_DIR, empty_dir)
    assert matrix["with_parity_test"] == 0
    # Implementation coverage unchanged from the real run
    assert matrix["implemented"] > 0


def test_class_with_no_python_module_is_not_implemented(tmp_path: Path) -> None:
    """Removing python_module entirely (None) makes has_python_impl False."""
    fake_mappings = tmp_path / "mappings"
    shutil.copytree(MAPPINGS_DIR, fake_mappings)

    classes_path = fake_mappings / "classes.json"
    classes = json.loads(classes_path.read_text())
    for entry in classes:
        if entry.get("unity_class") == "Camera":
            entry.pop("python_module", None)
            entry.pop("python_class", None)
    classes_path.write_text(json.dumps(classes))

    matrix = build_matrix(fake_mappings, PARITY_TESTS_DIR)
    row = _find_row(matrix, "Camera")
    assert row["has_python_impl"] is False
