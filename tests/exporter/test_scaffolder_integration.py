"""Integration tests for Unity project scaffolder (RED phase — module does not exist yet).

These tests run the full pipeline: translate Python example -> scaffold Unity project ->
verify structural validity of C# files in their final locations.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.exporter.project_scaffolder import scaffold_project
from src.translator.project_translator import translate_project
from src.gates.structural_gate import validate_csharp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

BREAKOUT_DIR = Path(__file__).resolve().parents[2] / "examples" / "breakout" / "breakout_python"


@pytest.fixture
def breakout_cs_files() -> dict[str, str]:
    """Translate the Breakout example to C# via project_translator."""
    return translate_project(str(BREAKOUT_DIR))


# ---------------------------------------------------------------------------
# Full pipeline: translate -> scaffold -> gate
# ---------------------------------------------------------------------------

class TestBreakoutScaffoldPipeline:
    """Translate Breakout, scaffold a Unity project, verify all C# files pass structural gate."""

    def test_all_cs_files_pass_structural_gate(self, tmp_path, breakout_cs_files):
        """Every .cs file in the scaffolded project must parse without errors."""
        scaffold_project("breakout", tmp_path, cs_files=breakout_cs_files)
        scripts_dir = tmp_path / "Assets" / "_Project" / "Scripts"
        assert scripts_dir.is_dir(), "Scripts directory must exist after scaffolding"

        cs_files = list(scripts_dir.glob("*.cs"))
        assert len(cs_files) > 0, "At least one .cs file must be scaffolded"

        failures = []
        for cs_file in cs_files:
            source = cs_file.read_text(encoding="utf-8")
            result = validate_csharp(source)
            if not result.valid:
                failures.append(f"{cs_file.name}: {result.errors[:3]}")

        assert not failures, (
            f"Structural gate failures in scaffolded project:\n"
            + "\n".join(failures)
        )

    def test_breakout_produces_multiple_scripts(self, tmp_path, breakout_cs_files):
        """Breakout has multiple Python files — all should become .cs scripts."""
        scaffold_project("breakout", tmp_path, cs_files=breakout_cs_files)
        scripts_dir = tmp_path / "Assets" / "_Project" / "Scripts"
        cs_files = list(scripts_dir.glob("*.cs"))
        # Breakout has: paddle_controller, ball_controller, brick, powerup, game_manager
        assert len(cs_files) >= 4, (
            f"Expected at least 4 C# files from Breakout, got {len(cs_files)}: "
            f"{[f.name for f in cs_files]}"
        )

    def test_no_init_cs_in_output(self, tmp_path, breakout_cs_files):
        """__init__.cs must never appear even if translator produces it."""
        scaffold_project("breakout", tmp_path, cs_files=breakout_cs_files)
        scripts_dir = tmp_path / "Assets" / "_Project" / "Scripts"
        assert not (scripts_dir / "__init__.cs").exists()


# ---------------------------------------------------------------------------
# Package detection integration
# ---------------------------------------------------------------------------

class TestPackageDetectionIntegration:
    """Packages/manifest.json must include packages detected by the translator."""

    def test_manifest_includes_input_system_when_detected(self, tmp_path):
        """If translator detects Input System usage, manifest must include it."""
        cs_files = {
            "PlayerInput.cs": (
                "using UnityEngine;\n"
                "using UnityEngine.InputSystem;\n"
                "public class PlayerInput : MonoBehaviour\n"
                "{\n    void OnMove(InputValue value) { }\n}\n"
            ),
            "_required_packages.json": json.dumps([
                {
                    "package": "com.unity.inputsystem",
                    "reason": "using UnityEngine.InputSystem",
                    "source_file": "PlayerInput.cs",
                },
            ]),
        }
        scaffold_project("test_input", tmp_path, cs_files=cs_files)
        manifest = tmp_path / "Packages" / "manifest.json"
        assert manifest.is_file()
        data = json.loads(manifest.read_text(encoding="utf-8"))
        deps = data.get("dependencies", {})
        assert "com.unity.inputsystem" in deps, (
            "Input System package must appear in manifest when translator detects it"
        )

    def test_manifest_includes_urp_by_default(self, tmp_path):
        """URP should always be included (all games use it)."""
        cs_files = {
            "Minimal.cs": "using UnityEngine;\npublic class Minimal : MonoBehaviour { }\n",
        }
        scaffold_project("minimal", tmp_path, cs_files=cs_files)
        manifest = tmp_path / "Packages" / "manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        deps = data.get("dependencies", {})
        assert "com.unity.render-pipelines.universal" in deps

    def test_breakout_packages_wired_into_manifest(self, tmp_path, breakout_cs_files):
        """Packages detected from Breakout translation must appear in the manifest."""
        scaffold_project("breakout", tmp_path, cs_files=breakout_cs_files)
        manifest = tmp_path / "Packages" / "manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        deps = data.get("dependencies", {})
        # URP is always expected
        assert "com.unity.render-pipelines.universal" in deps

        # If _required_packages.json exists in translator output, all must be in manifest
        pkg_json = breakout_cs_files.get("_required_packages.json")
        if pkg_json:
            required = json.loads(pkg_json)
            for pkg_info in required:
                pkg_name = pkg_info["package"]
                assert pkg_name in deps, (
                    f"Translator-detected package '{pkg_name}' missing from manifest"
                )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Edge case handling in the scaffolder."""

    def test_empty_cs_files_dict(self, tmp_path):
        """Scaffolding with no C# files should still create the directory structure."""
        scaffold_project("empty_game", tmp_path, cs_files={})
        assert (tmp_path / "Assets" / "_Project" / "Scripts").is_dir()
        assert (tmp_path / "Packages" / "manifest.json").is_file()

    def test_game_name_used_in_project(self, tmp_path):
        """The game name should appear somewhere in the project (e.g. product name)."""
        cs_files = {
            "Main.cs": "using UnityEngine;\npublic class Main : MonoBehaviour { }\n",
        }
        scaffold_project("my_awesome_game", tmp_path, cs_files=cs_files)
        # Check ProjectSettings for the game name
        settings_dir = tmp_path / "ProjectSettings"
        found = False
        for f in settings_dir.iterdir():
            if f.is_file():
                content = f.read_text(encoding="utf-8", errors="replace")
                if "my_awesome_game" in content.lower():
                    found = True
                    break
        assert found, "Game name should appear in ProjectSettings files"
