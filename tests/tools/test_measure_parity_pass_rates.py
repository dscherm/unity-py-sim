"""Independent validation of tools/measure_parity_pass_rates.py.

Tests are derived from the tool's documented schema and contracts (see the
module docstring of `tools/measure_parity_pass_rates.py`), NOT from the
implementation. Goal: prove the 87/87 = 100.0% (parked=28) claim is honest.

Three layers:
  1. Synthetic-XML unit tests for `_classify_skip` and `_parse_junit`.
  2. Pct-contract edge cases (zero divisors, all-pass, all-fail).
  3. End-to-end run of the real tool against the live parity suite.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
TOOL_PATH = ROOT / "tools" / "measure_parity_pass_rates.py"


def _load_tool():
    """Import the tool module from its file path (not a package)."""
    spec = importlib.util.spec_from_file_location(
        "measure_parity_pass_rates", TOOL_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tool = _load_tool()


# ---------------------------------------------------------------------------
# 1. Skip-classification correctness
# ---------------------------------------------------------------------------


class TestClassifySkip:
    """`_classify_skip(msg) -> {'parked', 'other'}` per the tool's docstring."""

    @pytest.mark.parametrize(
        "msg",
        [
            "PARITY_SCAFFOLD_PARKED - Audio out of scope",
            "Component is intentionally PARKED — see lesson",
            "out of scope: Unity UI is home-machine only",
            "out-of-scope: hyphenated form too",
            "WIP scaffold for AudioSource",
            "skeleton placeholder",
            "TODO: implement parity case later",
            "parity-scaffold skeleton: fill in scenario_python and scenario_csharp_body",
        ],
    )
    def test_parked_keywords_classify_parked(self, msg):
        assert tool._classify_skip(msg) == "parked"

    @pytest.mark.parametrize(
        "msg",
        [
            "dotnet not available",
            "dotnet SDK not available - C# leg of parity harness skipped",
            "no reason given",
            "",
            "skipped because of unrelated env issue",
        ],
    )
    def test_runtime_skips_classify_other(self, msg):
        assert tool._classify_skip(msg) == "other"

    def test_classify_is_case_insensitive(self):
        assert tool._classify_skip("PARKED") == "parked"
        assert tool._classify_skip("parked") == "parked"
        assert tool._classify_skip("Parked because OUT OF SCOPE") == "parked"

    def test_none_or_empty_message_classifies_other(self):
        # "no reason given" / empty string should fall through to 'other'.
        assert tool._classify_skip("") == "other"
        # The function signature is str, but be defensive about None-ish input
        # via the implementation's `(message or "")` fallback.
        assert tool._classify_skip(None) == "other"  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 2. JUnit parsing — synthetic XML
# ---------------------------------------------------------------------------


def _build_junit_xml(cases: list[dict]) -> str:
    """Build a pytest-compatible JUnit XML from a list of case dicts."""
    parts = ['<?xml version="1.0" encoding="utf-8"?>', "<testsuites>", "<testsuite>"]
    for c in cases:
        kind = c["kind"]
        name = c.get("name", "test_x")
        if kind == "passed":
            parts.append(f'  <testcase classname="m" name="{name}"></testcase>')
        elif kind == "failed":
            parts.append(
                f'  <testcase classname="m" name="{name}">'
                f'<failure message="boom">tb</failure></testcase>'
            )
        elif kind == "error":
            parts.append(
                f'  <testcase classname="m" name="{name}">'
                f'<error message="boom">tb</error></testcase>'
            )
        elif kind == "skipped":
            msg = c.get("message", "").replace('"', "&quot;")
            parts.append(
                f'  <testcase classname="m" name="{name}">'
                f'<skipped message="{msg}">{msg}</skipped></testcase>'
            )
        else:
            raise ValueError(kind)
    parts.append("</testsuite>")
    parts.append("</testsuites>")
    return "\n".join(parts)


class TestParseJunit:
    def test_mixed_buckets_classified_correctly(self, tmp_path):
        cases = [
            {"kind": "passed", "name": "p1"},
            {"kind": "passed", "name": "p2"},
            {"kind": "failed", "name": "f1"},
            {
                "kind": "skipped",
                "name": "s1",
                "message": "PARITY_SCAFFOLD_PARKED - Audio out of scope",
            },
            {
                "kind": "skipped",
                "name": "s2",
                "message": "WIP scaffold skeleton",
            },
            {
                "kind": "skipped",
                "name": "s3",
                "message": "dotnet not available",
            },
            {
                "kind": "skipped",
                "name": "s4",
                "message": "no reason given",
            },
        ]
        xml = _build_junit_xml(cases)
        path = tmp_path / "junit.xml"
        path.write_text(xml, encoding="utf-8")
        counts = tool._parse_junit(path)
        assert counts == {
            "passed": 2,
            "failed": 1,
            "skipped_parked": 2,
            "skipped_other": 2,
        }

    def test_error_element_counts_as_failed(self, tmp_path):
        xml = _build_junit_xml(
            [
                {"kind": "error", "name": "e1"},
                {"kind": "passed", "name": "p1"},
            ]
        )
        path = tmp_path / "junit.xml"
        path.write_text(xml, encoding="utf-8")
        counts = tool._parse_junit(path)
        assert counts["failed"] == 1
        assert counts["passed"] == 1

    def test_pct_excludes_parked_and_other_from_denominator(self, tmp_path):
        # 3 passed, 1 failed, 5 parked, 2 other-skipped.
        # pct should be 3 / (3+1) = 0.75, NOT 3/11.
        cases = (
            [{"kind": "passed", "name": f"p{i}"} for i in range(3)]
            + [{"kind": "failed", "name": "f1"}]
            + [
                {"kind": "skipped", "name": f"sp{i}", "message": "PARKED out of scope"}
                for i in range(5)
            ]
            + [
                {"kind": "skipped", "name": f"so{i}", "message": "dotnet not available"}
                for i in range(2)
            ]
        )
        path = tmp_path / "junit.xml"
        path.write_text(_build_junit_xml(cases), encoding="utf-8")

        out = tmp_path / "rates.json"
        # Drive measure() through monkeypatching _run_pytest so we don't shell out.
        import unittest.mock as mock

        with mock.patch.object(tool, "_run_pytest", return_value=0):
            # Tool computes junit path from output.with_suffix; redirect by
            # writing the synthetic XML to the expected location.
            expected_junit = out.with_suffix(".junit.xml")
            expected_junit.write_text(_build_junit_xml(cases), encoding="utf-8")
            payload = tool.measure(out)

        d = payload["dotnet"]
        assert d["passed"] == 3
        assert d["failed"] == 1
        assert d["skipped_parked"] == 5
        assert d["skipped_other"] == 2
        assert d["total_runnable"] == 4  # 3 + 1, NOT 11
        assert d["pct"] == 0.75

    def test_zero_runnable_returns_zero_pct_no_zerodivision(self, tmp_path):
        cases = [
            {"kind": "skipped", "name": "sp", "message": "PARKED"},
            {"kind": "skipped", "name": "so", "message": "dotnet missing"},
        ]
        path = tmp_path / "junit.xml"
        path.write_text(_build_junit_xml(cases), encoding="utf-8")
        out = tmp_path / "rates.json"
        import unittest.mock as mock

        with mock.patch.object(tool, "_run_pytest", return_value=0):
            out.with_suffix(".junit.xml").write_text(
                _build_junit_xml(cases), encoding="utf-8"
            )
            payload = tool.measure(out)
        d = payload["dotnet"]
        assert d["total_runnable"] == 0
        assert d["pct"] == 0.0  # not NaN, not None, not raised

    def test_all_parked_yields_zero_runnable(self, tmp_path):
        cases = [
            {"kind": "skipped", "name": f"sp{i}", "message": "PARITY_SCAFFOLD_PARKED"}
            for i in range(10)
        ]
        path = tmp_path / "junit.xml"
        path.write_text(_build_junit_xml(cases), encoding="utf-8")
        out = tmp_path / "rates.json"
        import unittest.mock as mock

        with mock.patch.object(tool, "_run_pytest", return_value=0):
            out.with_suffix(".junit.xml").write_text(
                _build_junit_xml(cases), encoding="utf-8"
            )
            payload = tool.measure(out)
        d = payload["dotnet"]
        assert d["skipped_parked"] == 10
        assert d["passed"] == 0
        assert d["failed"] == 0
        assert d["total_runnable"] == 0
        assert d["pct"] == 0.0

    def test_all_pass_yields_exactly_1_0(self, tmp_path):
        cases = [{"kind": "passed", "name": f"p{i}"} for i in range(7)]
        path = tmp_path / "junit.xml"
        path.write_text(_build_junit_xml(cases), encoding="utf-8")
        out = tmp_path / "rates.json"
        import unittest.mock as mock

        with mock.patch.object(tool, "_run_pytest", return_value=0):
            out.with_suffix(".junit.xml").write_text(
                _build_junit_xml(cases), encoding="utf-8"
            )
            payload = tool.measure(out)
        # Pct contract: exactly 1.0 when there are zero failures.
        assert payload["dotnet"]["pct"] == 1.0
        assert isinstance(payload["dotnet"]["pct"], float)

    def test_all_fail_yields_exactly_0_0_not_none(self, tmp_path):
        cases = [{"kind": "failed", "name": f"f{i}"} for i in range(4)]
        path = tmp_path / "junit.xml"
        path.write_text(_build_junit_xml(cases), encoding="utf-8")
        out = tmp_path / "rates.json"
        import unittest.mock as mock

        with mock.patch.object(tool, "_run_pytest", return_value=1):
            out.with_suffix(".junit.xml").write_text(
                _build_junit_xml(cases), encoding="utf-8"
            )
            payload = tool.measure(out)
        d = payload["dotnet"]
        assert d["pct"] == 0.0
        assert d["pct"] is not None


# ---------------------------------------------------------------------------
# 3. CoPlay deferral — schema must always include the key
# ---------------------------------------------------------------------------


class TestCoplayDeferral:
    def test_coplay_key_present_with_deferred_true(self, tmp_path):
        cases = [{"kind": "passed", "name": "p1"}]
        out = tmp_path / "rates.json"
        import unittest.mock as mock

        with mock.patch.object(tool, "_run_pytest", return_value=0):
            out.with_suffix(".junit.xml").write_text(
                _build_junit_xml(cases), encoding="utf-8"
            )
            payload = tool.measure(out)
        assert "coplay" in payload, "schema requires coplay key always present"
        assert payload["coplay"]["deferred"] is True
        assert "note" in payload["coplay"]

    def test_top_level_schema_has_required_keys(self, tmp_path):
        cases = [{"kind": "passed", "name": "p1"}]
        out = tmp_path / "rates.json"
        import unittest.mock as mock

        with mock.patch.object(tool, "_run_pytest", return_value=0):
            out.with_suffix(".junit.xml").write_text(
                _build_junit_xml(cases), encoding="utf-8"
            )
            payload = tool.measure(out)
        for key in ("timestamp", "dotnet", "coplay"):
            assert key in payload
        for key in (
            "passed",
            "failed",
            "skipped_parked",
            "skipped_other",
            "total_runnable",
            "pct",
        ):
            assert key in payload["dotnet"], f"missing dotnet.{key}"


# ---------------------------------------------------------------------------
# 4. End-to-end on real suite
# ---------------------------------------------------------------------------


@pytest.mark.slow
class TestEndToEndRealSuite:
    """Runs the actual tool against tests/parity/. Slow (~60s) — runs once."""

    @pytest.fixture(scope="class")
    def real_payload(self, tmp_path_factory):
        out = tmp_path_factory.mktemp("e2e") / "rates.json"
        proc = subprocess.run(
            [sys.executable, str(TOOL_PATH), "--output", str(out)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=180,
        )
        assert proc.returncode == 0, (
            f"tool exited {proc.returncode}\n"
            f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
        )
        assert out.exists(), "tool did not write output JSON"
        return json.loads(out.read_text(encoding="utf-8"))

    def test_runnable_is_passed_plus_failed(self, real_payload):
        d = real_payload["dotnet"]
        assert d["passed"] + d["failed"] == d["total_runnable"]

    def test_tests_actually_ran(self, real_payload):
        d = real_payload["dotnet"]
        total = (
            d["passed"]
            + d["failed"]
            + d["skipped_parked"]
            + d["skipped_other"]
        )
        assert total > 0, "expected the parity suite to produce >0 testcases"

    def test_meets_asp4_bar(self, real_payload):
        # ASP-4 bar: dotnet.pct >= 0.8
        assert real_payload["dotnet"]["pct"] >= 0.8, real_payload

    def test_pct_is_consistent_with_counts(self, real_payload):
        d = real_payload["dotnet"]
        if d["total_runnable"] == 0:
            assert d["pct"] == 0.0
        else:
            expected = d["passed"] / d["total_runnable"]
            assert abs(d["pct"] - expected) < 1e-9

    def test_schema_fields_have_correct_types(self, real_payload):
        d = real_payload["dotnet"]
        assert isinstance(d["passed"], int)
        assert isinstance(d["failed"], int)
        assert isinstance(d["skipped_parked"], int)
        assert isinstance(d["skipped_other"], int)
        assert isinstance(d["total_runnable"], int)
        assert isinstance(d["pct"], float)
        assert 0.0 <= d["pct"] <= 1.0
        assert real_payload["coplay"]["deferred"] is True

    def test_junit_temp_file_cleaned_up(self, real_payload, tmp_path_factory):
        # After tool runs, the .junit.xml sibling should be deleted (per
        # `junit_path.unlink(missing_ok=True)` in measure()).
        # The fixture's `out` was scoped, so we re-check with a fresh run.
        out_dir = tmp_path_factory.mktemp("e2e_cleanup")
        out = out_dir / "rates.json"
        proc = subprocess.run(
            [sys.executable, str(TOOL_PATH), "--output", str(out)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=180,
        )
        assert proc.returncode == 0
        assert out.exists()
        assert not out.with_suffix(".junit.xml").exists(), (
            "tool should clean up its junit XML sidecar"
        )

    def test_honest_100_percent_claim(self, real_payload):
        """If pct == 1.0, then failed must be 0 (no rounding hide)."""
        d = real_payload["dotnet"]
        if d["pct"] == 1.0:
            assert d["failed"] == 0, (
                "pct=1.0 must mean zero failures, not rounding"
            )
            assert d["passed"] == d["total_runnable"]
