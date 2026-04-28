"""Contract tests for the Gap Gate (M-12).

These tests are derived from the gate's CONTRACT (per plan.md and the
implementer's docstring), NOT from reading the implementer's own tests in
`tests/gates/test_gap_gate.py`. The contracts under test:

  C1. Grandfather only untouched code: files NOT in the diff are exempt; their
      uncovered API references must NOT show up in the gate report.
  C2. Strict on touched files: even if a touched file's reference predates the
      touch, an uncovered API must show up.
  C3. Auto-skeleton on miss: when scaffold=True (or in dry-run), the expected
      skeleton path under PARITY_TESTS_DIR is returned in
      result.skeletons_written for each untested API.
  C4. Exit codes: 0 when no untested references in touched files; 1 when
      uncovered APIs are found.

Validation lane: do NOT modify src/ or tools/. Tests only.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.gates import gap_gate
from src.gates.gap_gate import (
    APIReference,
    _expected_skeleton_paths,
    _untested_set,
    main,
    run_gate,
)


# Synthetic matrix used for tightly-controlled contract assertions.
# Keep it minimal so the tests don't accidentally depend on the live matrix.
_SYNTHETIC_MATRIX = {
    "rows": [
        # A class-level row that IS parity-tested.
        {
            "unity_class": "Transform",
            "unity_member": "",
            "kind": "class",
            "python_class": "Transform",
            "python_module": "src.engine.transform",
            "python_member": None,
            "has_python_impl": True,
            "has_parity_test": True,
        },
        # A property that IS parity-tested.
        {
            "unity_class": "Transform",
            "unity_member": "position",
            "kind": "property",
            "python_class": None,
            "python_module": None,
            "python_member": "position",
            "has_python_impl": True,
            "has_parity_test": True,
        },
        # The same class with an UNTESTED property — used to prove the gate
        # surfaces uncovered APIs in touched files.
        {
            "unity_class": "Transform",
            "unity_member": "Translate",
            "kind": "method",
            "python_class": None,
            "python_module": None,
            "python_member": "translate",
            "has_python_impl": True,
            "has_parity_test": False,
        },
    ]
}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers — write a synthetic Python source file and patch the matrix.


@pytest.fixture
def synthetic_repo(tmp_path, monkeypatch):
    """Build a tiny fake src/ tree under tmp_path with two python files:
    `touched.py` references the untested API; `untouched.py` references the
    same untested API but should NOT show up if it's not in the file list.
    """
    src_dir = tmp_path / "src" / "engine"
    src_dir.mkdir(parents=True)
    touched = src_dir / "touched.py"
    touched.write_text(
        "from src.engine.transform import Transform\n"
        "def go(t: Transform):\n"
        "    t.translate(1, 0, 0)\n"
        "    return t.position\n",
        encoding="utf-8",
    )
    untouched = src_dir / "untouched.py"
    untouched.write_text(
        "from src.engine.transform import Transform\n"
        "def stale(t: Transform):\n"
        "    return t.translate(0, 1, 0)\n",
        encoding="utf-8",
    )

    parity_dir = tmp_path / "tests" / "parity"
    parity_dir.mkdir(parents=True)

    # Patch module-level constants to point at the synthetic tree.
    monkeypatch.setattr(gap_gate, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gap_gate, "PARITY_TESTS_DIR", parity_dir)

    # Patch matrix loading.
    monkeypatch.setattr(gap_gate, "_load_matrix", lambda: _SYNTHETIC_MATRIX)

    return {
        "root": tmp_path,
        "touched": touched,
        "untouched": untouched,
        "parity_dir": parity_dir,
    }


# ─────────────────────────────────────────────────────────────────────────────
# C1. Grandfather only untouched code.


def test_untouched_files_are_grandfathered(synthetic_repo):
    """Untouched.py's uncovered API reference must NOT show up in the report
    when only touched.py is in the diff. This is the core of the
    'grandfather only untouched code' rule."""
    result = run_gate(
        base=None,
        files=["src/engine/touched.py"],
        scaffold=False,
    )
    untested_apis = {(r.unity_class, r.unity_member) for r in result.untested}
    assert ("Transform", "Translate") in untested_apis, (
        "touched.py references Transform.Translate — should be untested"
    )
    # Must come from touched.py, NOT untouched.py — assert the file attr.
    for u in result.untested:
        if (u.unity_class, u.unity_member) == ("Transform", "Translate"):
            assert "touched.py" in str(u.file)
            assert "untouched.py" not in str(u.file)


def test_no_diff_means_no_references(synthetic_repo):
    """When no files are touched, the gate has nothing to report — even if the
    matrix has untested APIs and the codebase mentions them."""
    result = run_gate(base=None, files=[], scaffold=False)
    assert result.references == []
    assert result.untested == []
    assert result.skeletons_written == []


# ─────────────────────────────────────────────────────────────────────────────
# C2. Strict on touched files (even if reference predates the touch).


def test_touched_file_uncovered_api_surfaces(synthetic_repo):
    """The gate doesn't care WHEN the API reference was added — it only cares
    that the file is in the touched list and contains an untested reference."""
    result = run_gate(
        base=None,
        files=["src/engine/touched.py"],
        scaffold=False,
    )
    api_pairs = {(u.unity_class, u.unity_member) for u in result.untested}
    assert ("Transform", "Translate") in api_pairs

    # And the GateResult.references should include the tested ones too —
    # the gate scans EVERY API reference, not just untested ones.
    ref_pairs = {(r.unity_class, r.unity_member) for r in result.references}
    assert ("Transform", "position") in ref_pairs  # tested
    assert ("Transform", "Translate") in ref_pairs  # untested


def test_tested_apis_do_not_surface_as_untested(synthetic_repo):
    """A reference to a parity-tested API must NOT appear in `untested`."""
    result = run_gate(
        base=None,
        files=["src/engine/touched.py"],
        scaffold=False,
    )
    api_pairs = {(u.unity_class, u.unity_member) for u in result.untested}
    assert ("Transform", "position") not in api_pairs


# ─────────────────────────────────────────────────────────────────────────────
# C3. Auto-skeleton on miss.


def test_dry_run_returns_expected_skeleton_paths(synthetic_repo):
    """With scaffold=False (no_scaffold), `skeletons_written` should still be
    populated with the EXPECTED paths under PARITY_TESTS_DIR so the gate's
    failure message can point the agent at them. No file is actually written
    in dry-run mode."""
    result = run_gate(
        base=None,
        files=["src/engine/touched.py"],
        scaffold=False,
    )
    assert result.skeletons_written, "expected at least one skeleton path"
    # Path must live under the (patched) PARITY_TESTS_DIR.
    parity_dir = synthetic_repo["parity_dir"]
    for p in result.skeletons_written:
        assert parity_dir in p.parents, f"{p} not under {parity_dir}"
    # Filename naming convention is `test_<class_slug>_<member_slug>_parity.py`.
    names = {p.name for p in result.skeletons_written}
    assert "test_transform_translate_parity.py" in names

    # Verify NO file was actually written (dry-run path).
    on_disk = list(parity_dir.glob("*.py"))
    assert on_disk == [], f"dry-run wrote files: {on_disk}"


def test_expected_skeleton_paths_class_only(synthetic_repo, monkeypatch):
    """When the untested API is a class-level row (member == ''), the skeleton
    path uses the `_class_parity.py` suffix per the scaffolder convention."""
    # Patch the matrix so the only untested API is a class-only row.
    matrix = {
        "rows": [
            {
                "unity_class": "Widget",
                "unity_member": "",
                "kind": "class",
                "python_class": "Widget",
                "python_module": "src.engine.widget",
                "python_member": None,
                "has_python_impl": True,
                "has_parity_test": False,
            },
        ]
    }
    monkeypatch.setattr(gap_gate, "_load_matrix", lambda: matrix)
    src_dir = synthetic_repo["root"] / "src" / "engine"
    f = src_dir / "uses_widget.py"
    f.write_text("class Foo:\n    w: 'Widget' = None\n", encoding="utf-8")

    result = run_gate(
        base=None,
        files=["src/engine/uses_widget.py"],
        scaffold=False,
    )
    names = {p.name for p in result.skeletons_written}
    assert "test_widget_class_parity.py" in names


def test_no_skeletons_when_everything_tested(synthetic_repo, monkeypatch):
    """When all referenced APIs are parity-tested, skeletons_written is []."""
    matrix = {
        "rows": [
            {
                "unity_class": "Transform",
                "unity_member": "position",
                "kind": "property",
                "python_class": None,
                "python_module": None,
                "python_member": "position",
                "has_python_impl": True,
                "has_parity_test": True,
            },
        ]
    }
    monkeypatch.setattr(gap_gate, "_load_matrix", lambda: matrix)
    src_dir = synthetic_repo["root"] / "src" / "engine"
    f = src_dir / "all_tested.py"
    f.write_text(
        "from src.engine.transform import Transform\n"
        "def go(t: Transform):\n"
        "    return t.position\n",
        encoding="utf-8",
    )
    result = run_gate(
        base=None,
        files=["src/engine/all_tested.py"],
        scaffold=False,
    )
    assert result.untested == []
    assert result.skeletons_written == []


# ─────────────────────────────────────────────────────────────────────────────
# C4. Exit codes.


def test_exit_code_0_when_no_diff(synthetic_repo, monkeypatch):
    """Calling run_gate() with files=[] should hit the 'no API references in
    touched files' branch and return 0 from main()."""
    # Bypass argparse — call main() with a sentinel that forces files=[].
    # We achieve this by stubbing _changed_files to return [] for this run.
    monkeypatch.setattr(gap_gate, "_changed_files", lambda base, files: [])
    rc = main(["--no-scaffold"])
    assert rc == 0


def test_exit_code_1_when_untested_api_found(synthetic_repo):
    """Touched file with an untested API → exit 1."""
    rc = main(["--files", "src/engine/touched.py", "--no-scaffold"])
    assert rc == 1


def test_exit_code_0_when_all_tested(synthetic_repo, monkeypatch):
    """Touched file whose every reference is parity-tested → exit 0."""
    matrix = {
        "rows": [
            {
                "unity_class": "Transform",
                "unity_member": "",
                "kind": "class",
                "python_class": "Transform",
                "python_module": "src.engine.transform",
                "python_member": None,
                "has_python_impl": True,
                "has_parity_test": True,
            },
            {
                "unity_class": "Transform",
                "unity_member": "position",
                "kind": "property",
                "python_class": None,
                "python_module": None,
                "python_member": "position",
                "has_python_impl": True,
                "has_parity_test": True,
            },
        ]
    }
    monkeypatch.setattr(gap_gate, "_load_matrix", lambda: matrix)
    src_dir = synthetic_repo["root"] / "src" / "engine"
    f = src_dir / "tested_only.py"
    f.write_text(
        "from src.engine.transform import Transform\n"
        "def go(t: Transform):\n"
        "    return t.position\n",
        encoding="utf-8",
    )
    rc = main(["--files", "src/engine/tested_only.py", "--no-scaffold"])
    assert rc == 0


# ─────────────────────────────────────────────────────────────────────────────
# Helper-level contracts — _untested_set and _expected_skeleton_paths.


def test_untested_set_filters_to_only_untested():
    """_untested_set is the inner predicate used by the gate. It must filter
    the input pairs down to exactly those NOT in the matrix's tested set."""
    refs = {
        ("Transform", "position"),  # tested
        ("Transform", "Translate"),  # untested
        ("Transform", ""),  # tested (class row)
    }
    untested = _untested_set(refs, _SYNTHETIC_MATRIX)
    assert untested == {("Transform", "Translate")}


def test_expected_skeleton_paths_naming():
    """File-naming convention proves the gate stays in lockstep with the
    scaffolder. If a future renaming desyncs them, this test will catch it."""
    refs = [
        APIReference(file=Path("ignored.py"), unity_class="Transform", unity_member="Translate"),
        APIReference(file=Path("ignored.py"), unity_class="GameObject", unity_member=""),
    ]
    paths = _expected_skeleton_paths(refs)
    names = sorted(p.name for p in paths)
    assert names == [
        "test_gameobject_class_parity.py",
        "test_transform_translate_parity.py",
    ]
