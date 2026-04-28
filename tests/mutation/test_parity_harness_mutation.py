"""Mutation tests for the M-8 dual-path parity harness.

These tests do NOT consume the harness's existing parity cases. Instead, they
construct deliberately-broken `ParityCase` instances and prove the harness
catches divergences from both legs (Python and C#).

Per Unity docs:
  - Transform.position is a Vector3 in world space
    (https://docs.unity3d.com/ScriptReference/Transform-position.html)
  - Vector3 is serialized as [x, y, z] floats by the harness's Serialize()

Each test is independent of the others. All require `dotnet` to actually
exercise the C# leg — they skip cleanly otherwise.
"""

from __future__ import annotations

import pytest

from tests.parity._harness import ParityCase, assert_parity, dotnet_available

# Skip the entire module on machines without dotnet — the C# leg is the whole
# point. (The harness itself uses pytest.skip inside _run_csharp, but we'd
# rather flag the dotnet dependency at module level for visibility.)
pytestmark = pytest.mark.skipif(
    not dotnet_available(),
    reason="dotnet SDK not available — parity harness mutation tests require it",
)


def test_python_leg_divergence_is_caught() -> None:
    """If Python emits a wrong observable, harness must raise AssertionError.

    The C# leg returns the *correct* Unity value: Transform.position of a fresh
    GameObject is Vector3.zero. Python lies and says z=99. Harness should
    catch the mismatch.
    """
    case = ParityCase(
        name="mutation_python_wrong_position",
        scenario_python=lambda: {"position": [0.0, 0.0, 99.0]},
        scenario_csharp_body="""
            var go = new GameObject("mutant");
            var p = go.transform.position;
            observables["position"] = new[] { p.x, p.y, p.z };
        """,
    )
    with pytest.raises(AssertionError, match="Parity mismatch"):
        assert_parity(case)


def test_csharp_leg_divergence_is_caught() -> None:
    """If C# emits a wrong observable, harness must raise AssertionError.

    Python emits the truth (zero vector — Unity's documented default for a
    fresh Transform.position). C# emits a deliberate lie (7,7,7). Harness
    should catch the mismatch.
    """
    case = ParityCase(
        name="mutation_csharp_wrong_position",
        scenario_python=lambda: {"position": [0.0, 0.0, 0.0]},
        scenario_csharp_body="""
            observables["position"] = new[] { 7f, 7f, 7f };
        """,
    )
    with pytest.raises(AssertionError, match="Parity mismatch"):
        assert_parity(case)


def test_float_tolerance_respected() -> None:
    """A 1e-6 difference passes at default tol (1e-4) but fails at 1e-9."""
    # Default tolerance — should pass.
    permissive = ParityCase(
        name="mutation_tol_default_passes",
        scenario_python=lambda: {"position": [0.0, 0.0, 1e-6]},
        scenario_csharp_body="""
            observables["position"] = new[] { 0f, 0f, 0f };
        """,
        # float_tolerance defaults to 1e-4
    )
    # No exception expected.
    assert_parity(permissive)

    # Tight tolerance — same numbers, but now 1e-6 > 1e-9 so it must fail.
    strict = ParityCase(
        name="mutation_tol_strict_fails",
        scenario_python=lambda: {"position": [0.0, 0.0, 1e-6]},
        scenario_csharp_body="""
            observables["position"] = new[] { 0f, 0f, 0f };
        """,
        float_tolerance=1e-9,
    )
    with pytest.raises(AssertionError, match="Parity mismatch"):
        assert_parity(strict)


def test_type_mismatch_is_caught() -> None:
    """Python emits a list under key 'shape', C# emits a dict — must fail.

    The harness's _deep_equal compares dict-vs-dict and list-vs-list; a list
    on one side and dict on the other should fall through to the float-equal
    branch and return False (the dict isn't a float, the list isn't a float).
    """
    case = ParityCase(
        name="mutation_type_mismatch",
        scenario_python=lambda: {"shape": [1.0, 2.0, 3.0]},
        scenario_csharp_body="""
            var d = new Dictionary<string, object>();
            d["x"] = 1f;
            d["y"] = 2f;
            d["z"] = 3f;
            observables["shape"] = d;
        """,
    )
    with pytest.raises(AssertionError, match="Parity mismatch"):
        assert_parity(case)


def test_missing_key_is_caught() -> None:
    """Python emits two keys, C# emits one — must fail on key-set mismatch."""
    case = ParityCase(
        name="mutation_missing_key",
        scenario_python=lambda: {"a": 1, "b": 2},
        scenario_csharp_body="""
            observables["a"] = 1;
        """,
    )
    with pytest.raises(AssertionError, match="Parity mismatch"):
        assert_parity(case)


def test_csharp_build_failure_surfaces_cleanly() -> None:
    """Broken C# body must raise (RuntimeError or AssertionError), not pass.

    `undefined_symbol` doesn't exist — the C# compile must fail. The harness's
    _run_csharp() raises RuntimeError on nonzero exit. We accept either
    RuntimeError or AssertionError as long as something is raised — silent
    pass would be the actual bug we're guarding against.
    """
    case = ParityCase(
        name="mutation_broken_csharp",
        scenario_python=lambda: {"x": 1},
        scenario_csharp_body="""
            observables["x"] = undefined_symbol;
        """,
    )
    with pytest.raises((RuntimeError, AssertionError)):
        assert_parity(case)
