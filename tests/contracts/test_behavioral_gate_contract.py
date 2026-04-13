"""Contract tests for behavioral_gate.py and gate_pipeline.py (Tasks 16-17).

Verifies that the gate scripts run successfully as subprocesses and
produce expected output markers.
"""

import subprocess
import sys
import os
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.slow
class TestBehavioralGateContract:
    """Behavioral gate must run all 5 games and pass all checks."""

    def test_behavioral_gate_exit_code_zero(self):
        """behavioral_gate.py exits with code 0 (all games pass)."""
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "behavioral_gate.py")],
            capture_output=True, text=True, cwd=ROOT, timeout=120,
        )
        assert result.returncode == 0, (
            f"behavioral_gate.py failed with exit code {result.returncode}\n"
            f"stdout: {result.stdout[-500:]}\nstderr: {result.stderr[-500:]}"
        )

    def test_behavioral_gate_output_contains_passed(self):
        """behavioral_gate.py output contains 'BEHAVIORAL GATE PASSED'."""
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "behavioral_gate.py")],
            capture_output=True, text=True, cwd=ROOT, timeout=120,
        )
        combined = result.stdout + result.stderr
        assert "BEHAVIORAL GATE PASSED" in combined, (
            f"Expected 'BEHAVIORAL GATE PASSED' in output.\n"
            f"Got: {combined[-500:]}"
        )

    def test_behavioral_gate_checks_all_five_games(self):
        """behavioral_gate.py output mentions all 5 games."""
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "behavioral_gate.py")],
            capture_output=True, text=True, cwd=ROOT, timeout=120,
        )
        combined = result.stdout + result.stderr
        for game in ["pong", "breakout", "fsm_platformer", "angry_birds", "space_invaders"]:
            assert f"[{game}]" in combined, f"Game '{game}' not found in output"


@pytest.mark.slow
class TestGatePipelineContract:
    """Gate pipeline --quick must pass (tests + behavioral + playtest)."""

    def test_gate_pipeline_quick_exit_code_zero(self):
        """gate_pipeline.py --quick exits with code 0."""
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "gate_pipeline.py"), "--quick"],
            capture_output=True, text=True, cwd=ROOT, timeout=300,
        )
        assert result.returncode == 0, (
            f"gate_pipeline.py --quick failed with exit code {result.returncode}\n"
            f"stdout: {result.stdout[-500:]}\nstderr: {result.stderr[-500:]}"
        )

    def test_gate_pipeline_quick_output_contains_gate_passed(self):
        """gate_pipeline.py --quick output contains 'GATE PASSED'."""
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "gate_pipeline.py"), "--quick"],
            capture_output=True, text=True, cwd=ROOT, timeout=300,
        )
        combined = result.stdout + result.stderr
        assert "GATE PASSED" in combined, (
            f"Expected 'GATE PASSED' in output.\n"
            f"Got: {combined[-500:]}"
        )
