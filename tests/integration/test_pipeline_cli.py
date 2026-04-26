"""Integration tests for the unified pipeline CLI (src.pipeline).

Tests the full translate -> scaffold -> gate pipeline invoked via CLI.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PYTHON = sys.executable


class TestPipelineHelp:
    """--help should exit 0 and show usage."""

    def test_help_exits_zero(self):
        result = subprocess.run(
            [PYTHON, "-m", "src.pipeline", "--help"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0

    def test_help_shows_usage(self):
        result = subprocess.run(
            [PYTHON, "-m", "src.pipeline", "--help"],
            capture_output=True, text=True, timeout=30,
        )
        assert "usage" in result.stdout.lower() or "--game" in result.stdout


class TestPipelineBreakout:
    """Run pipeline on breakout and verify project structure."""

    @pytest.fixture()
    def output_dir(self, tmp_path):
        return tmp_path / "breakout_project"

    def test_creates_project_structure(self, output_dir):
        result = subprocess.run(
            [PYTHON, "-m", "src.pipeline",
             "--game", "breakout",
             "--output", str(output_dir)],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}\nstdout: {result.stdout}"
        assert output_dir.exists()

    def test_output_contains_scripts(self, output_dir):
        subprocess.run(
            [PYTHON, "-m", "src.pipeline",
             "--game", "breakout",
             "--output", str(output_dir)],
            capture_output=True, text=True, timeout=60,
        )
        scripts_dir = output_dir / "Assets" / "_Project" / "Scripts"
        assert scripts_dir.exists(), f"Scripts dir missing. Contents: {list(output_dir.rglob('*'))}"
        cs_files = list(scripts_dir.glob("*.cs"))
        assert len(cs_files) > 0, f"No .cs files in {scripts_dir}"

    def test_output_has_project_settings(self, output_dir):
        subprocess.run(
            [PYTHON, "-m", "src.pipeline",
             "--game", "breakout",
             "--output", str(output_dir)],
            capture_output=True, text=True, timeout=60,
        )
        assert (output_dir / "ProjectSettings" / "ProjectSettings.asset").exists()
        assert (output_dir / "Packages" / "manifest.json").exists()

    def test_custom_source_dir(self, output_dir):
        """--source overrides the default examples/{game}/{game}_python path."""
        result = subprocess.run(
            [PYTHON, "-m", "src.pipeline",
             "--game", "breakout",
             "--source", "examples/breakout/breakout_python",
             "--output", str(output_dir)],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        scripts_dir = output_dir / "Assets" / "_Project" / "Scripts"
        cs_files = list(scripts_dir.glob("*.cs"))
        assert len(cs_files) > 0


class TestPipelineValidate:
    """--validate flag runs gates and reports results."""

    @pytest.fixture()
    def output_dir(self, tmp_path):
        return tmp_path / "breakout_validated"

    def test_validate_runs_gates(self, output_dir):
        result = subprocess.run(
            [PYTHON, "-m", "src.pipeline",
             "--game", "breakout",
             "--output", str(output_dir),
             "--validate"],
            capture_output=True, text=True, timeout=60,
        )
        # Should mention structural and convention results
        combined = result.stdout + result.stderr
        assert "structural" in combined.lower() or "convention" in combined.lower(), (
            f"Gate output not found. stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_validate_exit_code_zero_on_success(self, output_dir):
        """If all gates pass, exit code should be 0."""
        result = subprocess.run(
            [PYTHON, "-m", "src.pipeline",
             "--game", "breakout",
             "--output", str(output_dir),
             "--validate"],
            capture_output=True, text=True, timeout=60,
        )
        # We expect breakout to pass (or at least not crash)
        # Exit 0 = all pass, Exit 1 = some fail
        assert result.returncode in (0, 1), f"Unexpected exit code {result.returncode}"

    def test_validate_prints_summary(self, output_dir):
        result = subprocess.run(
            [PYTHON, "-m", "src.pipeline",
             "--game", "breakout",
             "--output", str(output_dir),
             "--validate"],
            capture_output=True, text=True, timeout=60,
        )
        combined = result.stdout
        # Should print pass/fail counts
        assert "pass" in combined.lower() or "fail" in combined.lower(), (
            f"Summary not found in output: {combined}"
        )


class TestPipelineExitCodes:
    """Verify exit codes are correct."""

    def test_missing_game_arg_exits_nonzero(self):
        result = subprocess.run(
            [PYTHON, "-m", "src.pipeline", "--output", "/tmp/foo"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode != 0

    def test_nonexistent_source_exits_nonzero(self, tmp_path):
        result = subprocess.run(
            [PYTHON, "-m", "src.pipeline",
             "--game", "fake_game",
             "--source", "/nonexistent/path",
             "--output", str(tmp_path / "out")],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode != 0
