"""Mutation tests for the Gap Gate (M-12).

Goal: prove our contract tests have teeth by deliberately breaking the gate
and watching contract tests fail. We monkey-patch the gate's internals via
unittest.mock — we do NOT edit any src/ or tools/ files.

Each mutation test:
  1. Patches a key gate function so it lies (returns empty / always False).
  2. Re-runs the same scenario the contract test runs.
  3. Asserts the contract assertion now FAILS (proving the contract caught
     the regression).

If a mutation passes the contract test, that's a hole in our contracts.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from src.gates import gap_gate
from src.gates.gap_gate import run_gate

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BREAKOUT_RUN = "examples/breakout/run_breakout.py"


# ─────────────────────────────────────────────────────────────────────────────
# Helper — same synthetic repo fixture as the contract tests, inlined to
# preserve isolation (we don't import the contract module to avoid coupling).


_SYNTHETIC_MATRIX = {
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


@pytest.fixture
def synthetic_repo(tmp_path, monkeypatch):
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
    parity_dir = tmp_path / "tests" / "parity"
    parity_dir.mkdir(parents=True)
    monkeypatch.setattr(gap_gate, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gap_gate, "PARITY_TESTS_DIR", parity_dir)
    monkeypatch.setattr(gap_gate, "_load_matrix", lambda: _SYNTHETIC_MATRIX)
    return tmp_path


# ─────────────────────────────────────────────────────────────────────────────
# MUTATION 1: _untested_set returns the empty set (i.e. lies that everything
# is tested). The contract C1/C2/C3 tests all rely on detecting an untested
# API; this mutation should make them fail.


def test_mutation_untested_set_returns_empty_breaks_contracts(synthetic_repo):
    """If _untested_set returns set() unconditionally, run_gate.untested goes
    empty too — a real bug because uncovered APIs would silently slip through
    CI. Our contract tests must catch this."""

    # Sanity: BEFORE mutation, the gate sees Transform.Translate as untested.
    pre = run_gate(base=None, files=["src/engine/touched.py"], scaffold=False)
    api_pairs = {(u.unity_class, u.unity_member) for u in pre.untested}
    assert ("Transform", "Translate") in api_pairs, (
        "pre-mutation sanity check failed — gate isn't seeing the untested API"
    )

    # AFTER mutation: lie about coverage.
    with patch.object(gap_gate, "_untested_set", return_value=set()):
        post = run_gate(base=None, files=["src/engine/touched.py"], scaffold=False)
        # The contract test asserts ("Transform", "Translate") is in untested.
        # With this mutation, the assertion fails.
        post_pairs = {(u.unity_class, u.unity_member) for u in post.untested}
        with pytest.raises(AssertionError):
            assert ("Transform", "Translate") in post_pairs


def test_mutation_untested_set_returns_empty_flips_exit_code(synthetic_repo):
    """Same mutation, but proven via exit code: with the lie, main() returns
    0 (no untested) instead of the correct 1."""
    with patch.object(gap_gate, "_untested_set", return_value=set()):
        rc = gap_gate.main(["--files", "src/engine/touched.py", "--no-scaffold"])
        # Mutation should flip the exit code from 1 to 0 (i.e. silently pass).
        assert rc == 0, (
            f"mutation should flip exit code to 0; got {rc} — either the "
            f"contract is wrong or the mutation didn't take effect"
        )


# ─────────────────────────────────────────────────────────────────────────────
# MUTATION 2: _is_in_scope always returns False (filter out everything). This
# breaks the integration test against examples/breakout/run_breakout.py.


def test_mutation_is_in_scope_always_false_breaks_integration(tmp_path):
    """If _is_in_scope returns False for every path, every file gets filtered
    out before scanning. A synthetic file referencing Transform.Rotate (still
    deferred-untested per ASP-3) should fail the gate before mutation, and
    pass after."""
    synthetic = tmp_path / "src" / "synthetic_spinner.py"
    synthetic.parent.mkdir(parents=True, exist_ok=True)
    synthetic.write_text(
        "class Spinner:\n"
        "    def update(self, transform) -> None:\n"
        "        transform.rotate(0, 1, 0)\n",
        encoding="utf-8",
    )

    from src.gates.gap_gate import main as gate_main
    rc_before = gate_main(["--files", str(synthetic), "--no-scaffold"])
    assert rc_before == 1, (
        f"pre-mutation sanity check failed — expected 1, got {rc_before}"
    )

    with patch.object(gap_gate, "_is_in_scope", return_value=False):
        rc_after = gate_main(["--files", str(synthetic), "--no-scaffold"])
        assert rc_after == 0, (
            f"mutation should green the gate; got {rc_after}"
        )

    rc_restored = gate_main(["--files", str(synthetic), "--no-scaffold"])
    assert rc_restored == 1, (
        f"after restore, gate should be red again; got {rc_restored}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# MUTATION 3: _scan_file_for_apis returns the empty set (lies that no APIs
# are referenced). Identical observable effect to mutation 1 in this scenario,
# but at a different layer — proves contracts catch upstream regressions too.


def test_mutation_scan_file_returns_empty_breaks_contracts(synthetic_repo):
    """If _scan_file_for_apis returns set() unconditionally, run_gate sees no
    references at all — including no untested ones. main() takes the
    'no Unity API references in touched files' branch and returns 0."""

    pre = run_gate(base=None, files=["src/engine/touched.py"], scaffold=False)
    pre_pairs = {(u.unity_class, u.unity_member) for u in pre.untested}
    assert ("Transform", "Translate") in pre_pairs

    with patch.object(gap_gate, "_scan_file_for_apis", return_value=set()):
        rc = gap_gate.main(["--files", "src/engine/touched.py", "--no-scaffold"])
        assert rc == 0, f"mutation should silently green the gate; got {rc}"


# ─────────────────────────────────────────────────────────────────────────────
# MUTATION 4: _expected_skeleton_paths returns []. The dry-run skeleton-path
# contract (C3) asserts the path list is non-empty when there's an untested
# API. This mutation must break that contract.


def test_mutation_expected_skeleton_paths_empty_breaks_C3(synthetic_repo):
    """If _expected_skeleton_paths returns [], the failure message wouldn't
    point the agent at any skeleton file. Contract C3 catches this."""

    pre = run_gate(base=None, files=["src/engine/touched.py"], scaffold=False)
    assert pre.skeletons_written, "pre-mutation should have skeleton paths"

    with patch.object(gap_gate, "_expected_skeleton_paths", return_value=[]):
        post = run_gate(base=None, files=["src/engine/touched.py"], scaffold=False)
        # Contract C3 asserts skeletons_written is non-empty when there's an
        # untested API. The mutation makes it empty.
        with pytest.raises(AssertionError):
            assert post.skeletons_written, "expected at least one skeleton path"
