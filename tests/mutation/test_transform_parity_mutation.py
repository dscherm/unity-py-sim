"""Mutation tests for the M-9 Transform parity batch.

Goal: prove the parity harness has TEETH (catches divergences between Python
sim and stubbed-C# headless) AND SUBSTANCE (passes when both backends actually
agree). Three Transform APIs are exercised:

  - Transform.Translate
  - Transform.localScale
  - Transform.childCount

For each API we ship two mutation cases:
  1. divergence case — Python and C# legs deliberately produce different
     observables; `assert_parity` MUST raise an AssertionError mentioning
     "Parity mismatch".
  2. agreement case — Python and C# legs are written to produce the same
     observables; `assert_parity` MUST NOT raise.

The validation contract is derived from Unity docs (Transform.Translate,
Transform-localScale, Transform-childCount) and the harness contract in
`tests/parity/_harness.py`. We do not read the parity tests under
`tests/parity/test_transform_*` — that would bias us toward whatever
phrasings the implementing agent chose.
"""

from __future__ import annotations

import pytest

from src.engine.core import GameObject
from tests.parity._harness import ParityCase, assert_parity, dotnet_available

pytestmark = pytest.mark.skipif(
    not dotnet_available(), reason="dotnet SDK not available — parity harness needs C# leg"
)


# ---------------------------------------------------------------------------
# Translate
# ---------------------------------------------------------------------------


def test_translate_divergence_is_caught() -> None:
    """If Python applies (1,2,3) but C# applies (9,9,9), the harness must yell."""

    def python_leg() -> dict[str, object]:
        go = GameObject("translate_div")
        go.transform.translate(__import__("src.engine.math.vector", fromlist=["Vector3"]).Vector3(1, 2, 3))
        p = go.transform.position
        return {"x": float(p.x), "y": float(p.y), "z": float(p.z)}

    case = ParityCase(
        name="translate_divergence",
        scenario_python=python_leg,
        scenario_csharp_body="""
            var go = new GameObject("translate_div");
            // Deliberately wrong delta — should diverge from Python's (1,2,3).
            go.transform.Translate(new Vector3(9f, 9f, 9f));
            observables["x"] = go.transform.position.x;
            observables["y"] = go.transform.position.y;
            observables["z"] = go.transform.position.z;
        """,
    )
    with pytest.raises(AssertionError) as excinfo:
        assert_parity(case)
    assert "Parity mismatch" in str(excinfo.value)


def test_translate_agreement_passes() -> None:
    """When both legs apply (1,2,3) from origin, the harness must accept."""

    def python_leg() -> dict[str, object]:
        from src.engine.math.vector import Vector3

        go = GameObject("translate_ok")
        go.transform.translate(Vector3(1, 2, 3))
        p = go.transform.position
        return {"x": float(p.x), "y": float(p.y), "z": float(p.z)}

    case = ParityCase(
        name="translate_agreement",
        scenario_python=python_leg,
        scenario_csharp_body="""
            var go = new GameObject("translate_ok");
            go.transform.Translate(new Vector3(1f, 2f, 3f));
            observables["x"] = go.transform.position.x;
            observables["y"] = go.transform.position.y;
            observables["z"] = go.transform.position.z;
        """,
    )
    # Must not raise.
    assert_parity(case)


# ---------------------------------------------------------------------------
# localScale
# ---------------------------------------------------------------------------


def test_localscale_divergence_is_caught() -> None:
    """Python sets (2,3,4) but C# sets (1,1,1) — harness must catch."""

    def python_leg() -> dict[str, object]:
        from src.engine.math.vector import Vector3

        go = GameObject("scale_div")
        go.transform.local_scale = Vector3(2, 3, 4)
        s = go.transform.local_scale
        return {"sx": float(s.x), "sy": float(s.y), "sz": float(s.z)}

    case = ParityCase(
        name="localscale_divergence",
        scenario_python=python_leg,
        scenario_csharp_body="""
            var go = new GameObject("scale_div");
            // Default localScale is (1,1,1); we deliberately leave it alone
            // so it diverges from Python's (2,3,4).
            observables["sx"] = go.transform.localScale.x;
            observables["sy"] = go.transform.localScale.y;
            observables["sz"] = go.transform.localScale.z;
        """,
    )
    with pytest.raises(AssertionError) as excinfo:
        assert_parity(case)
    assert "Parity mismatch" in str(excinfo.value)


def test_localscale_agreement_passes() -> None:
    """Both legs assign localScale = (2,3,4); harness must accept."""

    def python_leg() -> dict[str, object]:
        from src.engine.math.vector import Vector3

        go = GameObject("scale_ok")
        go.transform.local_scale = Vector3(2, 3, 4)
        s = go.transform.local_scale
        return {"sx": float(s.x), "sy": float(s.y), "sz": float(s.z)}

    case = ParityCase(
        name="localscale_agreement",
        scenario_python=python_leg,
        scenario_csharp_body="""
            var go = new GameObject("scale_ok");
            go.transform.localScale = new Vector3(2f, 3f, 4f);
            observables["sx"] = go.transform.localScale.x;
            observables["sy"] = go.transform.localScale.y;
            observables["sz"] = go.transform.localScale.z;
        """,
    )
    assert_parity(case)


# ---------------------------------------------------------------------------
# childCount
# ---------------------------------------------------------------------------


def test_childcount_divergence_is_caught() -> None:
    """Python parents 3 children; C# parents only 1 — harness must catch."""

    def python_leg() -> dict[str, object]:
        parent = GameObject("parent_div")
        for i in range(3):
            child = GameObject(f"child_{i}")
            child.transform.set_parent(parent.transform)
        return {"count": int(parent.transform.child_count)}

    case = ParityCase(
        name="childcount_divergence",
        scenario_python=python_leg,
        scenario_csharp_body="""
            var parent = new GameObject("parent_div");
            // Deliberately attach only one child instead of three.
            var only = new GameObject("only_child");
            only.transform.SetParent(parent.transform);
            observables["count"] = parent.transform.childCount;
        """,
    )
    with pytest.raises(AssertionError) as excinfo:
        assert_parity(case)
    assert "Parity mismatch" in str(excinfo.value)


def test_childcount_agreement_passes() -> None:
    """Both legs parent 3 children; harness must accept."""

    def python_leg() -> dict[str, object]:
        parent = GameObject("parent_ok")
        for i in range(3):
            child = GameObject(f"child_{i}")
            child.transform.set_parent(parent.transform)
        return {"count": int(parent.transform.child_count)}

    case = ParityCase(
        name="childcount_agreement",
        scenario_python=python_leg,
        scenario_csharp_body="""
            var parent = new GameObject("parent_ok");
            for (int i = 0; i < 3; i++)
            {
                var child = new GameObject("child_" + i);
                child.transform.SetParent(parent.transform);
            }
            observables["count"] = parent.transform.childCount;
        """,
    )
    assert_parity(case)
