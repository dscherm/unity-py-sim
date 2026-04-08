"""Contract tests for Unity project scaffolder (RED phase — module does not exist yet).

Tests verify that scaffold_project() creates a valid Unity project folder structure
from translated C# output, matching the conventions in pacman_mapping.json's
project_structure section and standard Unity project layout.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.exporter.project_scaffolder import scaffold_project


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_cs_files() -> dict[str, str]:
    """Minimal set of translated C# files to scaffold with."""
    return {
        "GameManager.cs": "using UnityEngine;\npublic class GameManager : MonoBehaviour\n{\n    void Start() { }\n}\n",
        "PlayerController.cs": "using UnityEngine;\npublic class PlayerController : MonoBehaviour\n{\n    void Update() { }\n}\n",
        "_required_packages.json": json.dumps([
            {"package": "com.unity.render-pipelines.universal", "reason": "URP", "source_file": "GameManager.cs"},
        ]),
    }


@pytest.fixture
def sample_tags() -> list[str]:
    return ["Player", "Enemy", "Powerup"]


# ---------------------------------------------------------------------------
# Directory structure tests
# ---------------------------------------------------------------------------

class TestDirectoryStructure:
    """scaffold_project must create the standard Unity project directories."""

    EXPECTED_DIRS = [
        "Assets/_Project/Scripts",
        "Assets/_Project/Prefabs",
        "Assets/_Project/Scenes",
        "Assets/Art/Sprites",
        "Assets/Editor",
        "Packages",
        "ProjectSettings",
    ]

    def test_all_required_dirs_created(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        for rel in self.EXPECTED_DIRS:
            d = tmp_path / rel
            assert d.is_dir(), f"Expected directory not created: {rel}"

    def test_scripts_dir_matches_mapping_convention(self, tmp_path, sample_cs_files):
        """The scripts dir should match pacman_mapping.json project_structure.scripts_dir."""
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        assert (tmp_path / "Assets" / "_Project" / "Scripts").is_dir()

    def test_prefabs_dir_exists(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        assert (tmp_path / "Assets" / "_Project" / "Prefabs").is_dir()

    def test_scenes_dir_exists(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        assert (tmp_path / "Assets" / "_Project" / "Scenes").is_dir()


# ---------------------------------------------------------------------------
# ProjectSettings tests
# ---------------------------------------------------------------------------

class TestProjectSettings:
    """ProjectSettings/ must contain required Unity config files."""

    def test_project_version_txt_exists(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        pv = tmp_path / "ProjectSettings" / "ProjectVersion.txt"
        assert pv.is_file(), "ProjectVersion.txt must exist"

    def test_project_version_contains_editor_version(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        pv = tmp_path / "ProjectSettings" / "ProjectVersion.txt"
        content = pv.read_text(encoding="utf-8")
        assert "m_EditorVersion:" in content, "Must contain m_EditorVersion: line"

    def test_tag_manager_created_when_tags_provided(self, tmp_path, sample_cs_files, sample_tags):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files, tags=sample_tags)
        tm = tmp_path / "ProjectSettings" / "TagManager.asset"
        assert tm.is_file(), "TagManager.asset must exist when tags are provided"

    def test_tag_manager_contains_provided_tags(self, tmp_path, sample_cs_files, sample_tags):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files, tags=sample_tags)
        tm = tmp_path / "ProjectSettings" / "TagManager.asset"
        content = tm.read_text(encoding="utf-8")
        for tag in sample_tags:
            assert tag in content, f"Tag '{tag}' must appear in TagManager.asset"


# ---------------------------------------------------------------------------
# Packages/manifest.json tests
# ---------------------------------------------------------------------------

class TestPackagesManifest:
    """Packages/manifest.json must be valid JSON with required dependencies."""

    def test_manifest_exists(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        manifest = tmp_path / "Packages" / "manifest.json"
        assert manifest.is_file(), "Packages/manifest.json must exist"

    def test_manifest_is_valid_json(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        manifest = tmp_path / "Packages" / "manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_manifest_contains_urp(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        manifest = tmp_path / "Packages" / "manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        deps = data.get("dependencies", {})
        assert "com.unity.render-pipelines.universal" in deps, (
            "URP package must be in manifest dependencies"
        )

    def test_manifest_has_dependencies_key(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        manifest = tmp_path / "Packages" / "manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        assert "dependencies" in data, "manifest.json must have a 'dependencies' key"


# ---------------------------------------------------------------------------
# C# file placement tests
# ---------------------------------------------------------------------------

class TestCSharpFilePlacement:
    """Translated C# files must be copied into Assets/_Project/Scripts/."""

    def test_cs_files_placed_in_scripts_dir(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        scripts = tmp_path / "Assets" / "_Project" / "Scripts"
        assert (scripts / "GameManager.cs").is_file()
        assert (scripts / "PlayerController.cs").is_file()

    def test_cs_file_content_preserved(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        scripts = tmp_path / "Assets" / "_Project" / "Scripts"
        content = (scripts / "GameManager.cs").read_text(encoding="utf-8")
        assert "class GameManager" in content

    def test_init_cs_excluded(self, tmp_path):
        """__init__.cs and other non-class artifacts must not be written."""
        cs_files = {
            "GameManager.cs": "using UnityEngine;\npublic class GameManager : MonoBehaviour { }\n",
            "__init__.cs": "// auto-generated init\n",
        }
        scaffold_project("breakout", tmp_path, cs_files=cs_files)
        scripts = tmp_path / "Assets" / "_Project" / "Scripts"
        assert not (scripts / "__init__.cs").exists(), "__init__.cs must be excluded"

    def test_required_packages_json_excluded_from_scripts(self, tmp_path, sample_cs_files):
        """_required_packages.json is metadata, not a script file."""
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        scripts = tmp_path / "Assets" / "_Project" / "Scripts"
        assert not (scripts / "_required_packages.json").exists()

    def test_only_cs_files_in_scripts_dir(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        scripts = tmp_path / "Assets" / "_Project" / "Scripts"
        for f in scripts.iterdir():
            assert f.suffix == ".cs", f"Non-.cs file found in Scripts: {f.name}"


# ---------------------------------------------------------------------------
# CLI entry point tests
# ---------------------------------------------------------------------------

class TestCLIEntryPoint:
    """The scaffolder must be invocable as a CLI module."""

    def test_cli_module_importable(self):
        """python -m src.exporter.scaffold should be a valid entry point."""
        result = subprocess.run(
            [sys.executable, "-m", "src.exporter.scaffold", "--help"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parents[2]),
            timeout=30,
        )
        # Should exit 0 (help text) or at least not crash with ModuleNotFoundError
        assert result.returncode == 0, (
            f"CLI entry point failed: stderr={result.stderr[:500]}"
        )

    def test_cli_creates_project(self, tmp_path):
        result = subprocess.run(
            [
                sys.executable, "-m", "src.exporter.scaffold",
                "--game", "breakout",
                "--output", str(tmp_path / "unity_out"),
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parents[2]),
            timeout=60,
        )
        assert result.returncode == 0, (
            f"CLI scaffold failed: stderr={result.stderr[:500]}"
        )
        assert (tmp_path / "unity_out" / "Assets").is_dir()
