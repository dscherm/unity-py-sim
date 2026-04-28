"""Contract + integration tests for the M-7 phase 2 PlayMode scaffolding.

Verifies that scaffold_project emits everything Unity Test Framework needs
for `Unity -runTests -testPlatform PlayMode` to discover and run a single
[UnityTest] that ticks the active scene for ~3 seconds and fails on any
logged Error/Exception/Assert.
"""

from __future__ import annotations

import json

import pytest

from src.exporter.project_scaffolder import (
    _DEFAULT_PACKAGES,
    _PROJECT_DIRS,
    scaffold_project,
)


@pytest.fixture
def sample_cs_files() -> dict[str, str]:
    return {
        "GameManager.cs": (
            "using UnityEngine;\n"
            "public class GameManager : MonoBehaviour { void Start() {} }\n"
        ),
    }


class TestDefaults:
    """Verify the static config that drives the scaffold."""

    def test_test_framework_in_default_packages(self):
        assert "com.unity.test-framework" in _DEFAULT_PACKAGES, (
            "Test framework must be declared explicitly so [UnityTest] is "
            "reliably available without depending on transitive resolution."
        )

    def test_playmode_dir_in_project_dirs(self):
        assert "Assets/Tests/PlayMode" in _PROJECT_DIRS


class TestScaffoldedFiles:
    """Verify scaffold_project produces the test files on disk."""

    def test_playmode_test_cs_written(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        test_cs = tmp_path / "Assets" / "Tests" / "PlayMode" / "PlayModeTests.cs"
        assert test_cs.exists()
        body = test_cs.read_text(encoding="utf-8")
        assert "[UnityTest]" in body
        assert "public IEnumerator PlayForNSeconds_NoLoggedExceptions" in body
        # Game name interpolated into header for traceability
        assert "Game: breakout" in body

    def test_playmode_test_cs_meta_written(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        meta = tmp_path / "Assets" / "Tests" / "PlayMode" / "PlayModeTests.cs.meta"
        assert meta.exists()
        contents = meta.read_text(encoding="utf-8")
        assert "MonoImporter" in contents
        assert "guid:" in contents

    def test_playmode_test_asmdef_written(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        asmdef_path = (
            tmp_path / "Assets" / "Tests" / "PlayMode" / "PlayModeTests.asmdef"
        )
        assert asmdef_path.exists()
        data = json.loads(asmdef_path.read_text(encoding="utf-8"))
        assert data["name"] == "PlayModeTests"
        assert "UnityEngine.TestRunner" in data["references"]
        assert "UnityEditor.TestRunner" in data["references"]
        assert "nunit.framework.dll" in data["precompiledReferences"]
        # MUST be empty for PlayMode test discovery (`["Editor"]` would
        # scope it to Edit-mode tests and `-testPlatform PlayMode` would
        # report "No tests were executed.").
        assert data["includePlatforms"] == []
        # Tests must compile only when the test framework activates them,
        # otherwise prod player builds blow up trying to resolve nunit.
        assert "UNITY_INCLUDE_TESTS" in data["defineConstraints"]
        assert data["overrideReferences"] is True
        assert data["autoReferenced"] is False

    def test_playmode_test_asmdef_meta_written(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        meta = (
            tmp_path / "Assets" / "Tests" / "PlayMode" / "PlayModeTests.asmdef.meta"
        )
        assert meta.exists()
        contents = meta.read_text(encoding="utf-8")
        assert "AssemblyDefinitionImporter" in contents
        assert "guid:" in contents


class TestManifest:
    """Verify Packages/manifest.json picks up the test framework."""

    def test_manifest_declares_test_framework(self, tmp_path, sample_cs_files):
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        manifest = json.loads(
            (tmp_path / "Packages" / "manifest.json").read_text(encoding="utf-8")
        )
        assert "com.unity.test-framework" in manifest["dependencies"]


class TestGuidStability:
    """Determinism: regeneration must not churn the .meta GUIDs."""

    def test_asmdef_guid_stable_across_regens(self, tmp_path, sample_cs_files):
        out_a = tmp_path / "a"
        out_b = tmp_path / "b"
        scaffold_project("breakout", out_a, cs_files=sample_cs_files)
        scaffold_project("breakout", out_b, cs_files=sample_cs_files)
        meta_a = (out_a / "Assets/Tests/PlayMode/PlayModeTests.asmdef.meta").read_text("utf-8")
        meta_b = (out_b / "Assets/Tests/PlayMode/PlayModeTests.asmdef.meta").read_text("utf-8")
        # Pull guid line out — full file may have whitespace-only diffs
        guid_a = next(l for l in meta_a.splitlines() if l.startswith("guid:"))
        guid_b = next(l for l in meta_b.splitlines() if l.startswith("guid:"))
        assert guid_a == guid_b
