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

    def test_only_cs_and_meta_files_in_scripts_dir(self, tmp_path, sample_cs_files):
        """Scripts dir must contain only .cs (sources) and .meta (Unity script
        metadata, deterministic GUIDs — see flappy_bird_deploy.md gap 7).
        No other file types should leak in."""
        scaffold_project("breakout", tmp_path, cs_files=sample_cs_files)
        scripts = tmp_path / "Assets" / "_Project" / "Scripts"
        for f in scripts.iterdir():
            assert f.suffix in (".cs", ".meta"), (
                f"Unexpected file in Scripts: {f.name}"
            )


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


class TestAutoStartFixture:
    """AutoStart.cs is a generic runtime un-pauser written by the scaffolder.

    Covers data/lessons/flappy_bird_deploy.md gap 1: games whose
    GameManager.Start() calls Pause() (expecting a UI Play button to
    un-pause on click) are stuck because the PlayButtonHandler MonoBehaviour
    that wires the click lives inline in run_*.py and is filtered by the
    scene serializer's translated-class registry (coplay gap 4).  AutoStart
    is a runtime MonoBehaviour that reflectively finds GameManager.instance
    (or Instance) and invokes Play() on it.  Harmless for games without a
    GameManager.
    """

    def test_autostart_cs_written(self, tmp_path, sample_cs_files):
        scaffold_project("test", tmp_path, cs_files=sample_cs_files)
        autostart = tmp_path / "Assets" / "_Project" / "Scripts" / "AutoStart.cs"
        assert autostart.is_file(), "AutoStart.cs must be written to Scripts/"

    def test_autostart_is_monobehaviour(self, tmp_path, sample_cs_files):
        scaffold_project("test", tmp_path, cs_files=sample_cs_files)
        content = (tmp_path / "Assets" / "_Project" / "Scripts" / "AutoStart.cs").read_text(encoding="utf-8")
        assert "public class AutoStart : MonoBehaviour" in content
        assert "void Start()" in content

    def test_autostart_uses_reflection_for_gamemanager_singleton(self, tmp_path, sample_cs_files):
        """AutoStart must not hard-reference GameManager — must look it up
        reflectively so it compiles even for games without a GameManager."""
        scaffold_project("test", tmp_path, cs_files=sample_cs_files)
        content = (tmp_path / "Assets" / "_Project" / "Scripts" / "AutoStart.cs").read_text(encoding="utf-8")
        assert "System.Type.GetType" in content
        assert '"GameManager"' in content
        # Must probe both common singleton naming conventions
        assert '"instance"' in content
        assert '"Instance"' in content
        # Must invoke Play() via reflection, not a direct call
        assert '"Play"' in content

    def test_autostart_also_written_for_games_without_gamemanager(self, tmp_path):
        """Even without a GameManager.cs in the translated output, AutoStart
        still lands — it's a no-op at runtime because reflection returns early."""
        minimal = {"X.cs": "public class X {}\n"}
        scaffold_project("test", tmp_path, cs_files=minimal)
        autostart = tmp_path / "Assets" / "_Project" / "Scripts" / "AutoStart.cs"
        assert autostart.is_file()


class TestScriptMetaDeterministicGuid:
    """Gap 7 (data/lessons/flappy_bird_deploy.md): each .cs file must ship
    with a .cs.meta whose GUID matches the prefab_generator's m_Script
    reference scheme — `_deterministic_guid(f"script:{class_name}")`.

    Without this, Unity assigns a random GUID to each .cs on first import
    and the prefab's MonoBehaviour refs are dangling.  Symptom: spawned
    Pipes clones had no Pipes component attached, Update() never ran,
    pipes sat frozen at the spawn position.
    """

    def test_cs_meta_files_written(self, tmp_path, sample_cs_files):
        scaffold_project("test", tmp_path, cs_files=sample_cs_files)
        scripts = tmp_path / "Assets" / "_Project" / "Scripts"
        assert (scripts / "GameManager.cs.meta").is_file()
        assert (scripts / "PlayerController.cs.meta").is_file()

    def test_cs_meta_guid_matches_deterministic_scheme(self, tmp_path, sample_cs_files):
        """The .meta guid must equal prefab_generator's script:<class> GUID."""
        from src.exporter.prefab_generator import _deterministic_guid
        scaffold_project("test", tmp_path, cs_files=sample_cs_files)
        content = (tmp_path / "Assets" / "_Project" / "Scripts" / "GameManager.cs.meta").read_text(encoding="utf-8")
        expected = _deterministic_guid("script:GameManager")
        assert f"guid: {expected}" in content

    def test_prefab_monobehaviour_ref_resolves_to_same_guid(self, tmp_path, sample_cs_files):
        """Prefab m_Script guid must equal the scaffolded .cs.meta guid for
        the same class name — else Unity can't bind the script on import."""
        from src.exporter.prefab_generator import (
            _deterministic_guid,
            generate_prefab_yaml,
        )
        scaffold_project("test", tmp_path, cs_files=sample_cs_files)
        meta = (tmp_path / "Assets" / "_Project" / "Scripts" / "GameManager.cs.meta").read_text(encoding="utf-8")
        prefab = generate_prefab_yaml("GameManager", ["GameManager"])
        # Extract the guid from the meta; assert prefab m_Script uses it.
        for line in meta.splitlines():
            if line.startswith("guid: "):
                meta_guid = line.split("guid: ", 1)[1].strip()
                break
        else:
            raise AssertionError("Meta file has no guid: line")
        assert f"m_Script: {{fileID: 11500000, guid: {meta_guid}, type: 3}}" in prefab
        # Sanity: scheme matches both sides.
        assert meta_guid == _deterministic_guid("script:GameManager")

    def test_meta_is_mono_importer(self, tmp_path, sample_cs_files):
        """Unity expects MonoImporter block (not GenericImporter) for .cs."""
        scaffold_project("test", tmp_path, cs_files=sample_cs_files)
        content = (tmp_path / "Assets" / "_Project" / "Scripts" / "GameManager.cs.meta").read_text(encoding="utf-8")
        assert "MonoImporter:" in content
        assert "fileFormatVersion: 2" in content


class TestAspectLockFixture:
    """Gap 5 (data/lessons/flappy_bird_deploy.md): scaffolder writes
    AspectLock.cs so games with specific intended aspect ratios render in
    a letterboxed viewport regardless of Unity's Game view window size.
    """

    def test_aspect_lock_cs_written(self, tmp_path, sample_cs_files):
        scaffold_project("test", tmp_path, cs_files=sample_cs_files)
        lock = tmp_path / "Assets" / "_Project" / "Scripts" / "AspectLock.cs"
        assert lock.is_file(), "AspectLock.cs must be written to Scripts/"

    def test_aspect_lock_is_camera_monobehaviour(self, tmp_path, sample_cs_files):
        scaffold_project("test", tmp_path, cs_files=sample_cs_files)
        content = (tmp_path / "Assets" / "_Project" / "Scripts" / "AspectLock.cs").read_text(encoding="utf-8")
        assert "public class AspectLock : MonoBehaviour" in content
        assert "[RequireComponent(typeof(Camera))]" in content
        # Must expose a tunable targetAspect so landscape games can override.
        assert "public float targetAspect" in content

    def test_aspect_lock_handles_wider_and_narrower_windows(self, tmp_path, sample_cs_files):
        """Implementation must letterbox both directions — wider windows get
        top/bottom bars, narrower get left/right."""
        scaffold_project("test", tmp_path, cs_files=sample_cs_files)
        content = (tmp_path / "Assets" / "_Project" / "Scripts" / "AspectLock.cs").read_text(encoding="utf-8")
        # Applies to cam.rect (viewport), not to orthographicSize.
        assert "cam.rect" in content
        # Both branches present.
        assert "scaleHeight < 1f" in content
        assert "scaleWidth" in content


class TestPrefabGuidHealing:
    """scaffold_project post-step rewrites stale m_Script GUIDs in existing
    Prefabs/*.prefab to match the deterministic .cs.meta scheme.

    Covers the case where a Prefab was generated in an earlier session
    (or hand-created with a Unity-random GUID) and now drifts from the
    current scaffolder's .cs.meta GUID — the root cause behind Flappy
    Bird's "pipes don't move" symptom (data/lessons/flappy_bird_deploy.md
    gap 7 follow-on).
    """

    def test_heal_rewrites_stale_prefab_m_script(self, tmp_path, sample_cs_files):
        from src.exporter.prefab_generator import _deterministic_guid
        scripts = tmp_path / "Assets" / "_Project" / "Scripts"
        prefabs = tmp_path / "Assets" / "_Project" / "Prefabs"
        prefabs.mkdir(parents=True, exist_ok=True)
        # Write a stale PlayerController.prefab with a wrong GUID.
        stale_guid = "00000000000000000000000000000000"
        (prefabs / "PlayerController.prefab").write_text(
            "%YAML 1.1\n"
            "MonoBehaviour:\n"
            f"  m_Script: {{fileID: 11500000, guid: {stale_guid}, type: 3}}\n"
            "  m_Name: \n",
            encoding="utf-8",
        )
        # Now run the scaffolder — it writes PlayerController.cs.meta
        # with the deterministic guid AND heals the prefab to match.
        scaffold_project("test", tmp_path, cs_files=sample_cs_files)
        healed = (prefabs / "PlayerController.prefab").read_text(encoding="utf-8")
        expected = _deterministic_guid("script:PlayerController")
        assert stale_guid not in healed
        assert f"guid: {expected}" in healed

    def test_heal_no_op_when_guid_already_matches(self, tmp_path, sample_cs_files):
        from src.exporter.prefab_generator import _deterministic_guid
        scripts = tmp_path / "Assets" / "_Project" / "Scripts"
        prefabs = tmp_path / "Assets" / "_Project" / "Prefabs"
        prefabs.mkdir(parents=True, exist_ok=True)
        good = _deterministic_guid("script:PlayerController")
        content = (
            "%YAML 1.1\n"
            "MonoBehaviour:\n"
            f"  m_Script: {{fileID: 11500000, guid: {good}, type: 3}}\n"
            "  m_Name: \n"
        )
        (prefabs / "PlayerController.prefab").write_text(content, encoding="utf-8")
        scaffold_project("test", tmp_path, cs_files=sample_cs_files)
        # Unchanged.
        assert (prefabs / "PlayerController.prefab").read_text(encoding="utf-8") == content

    def test_heal_rewrites_null_fileid_prefab(self, tmp_path, sample_cs_files):
        """Prefabs from the pre-gap-7 generator have `m_Script: {fileID: 0}`
        (null ref).  Heal must replace that with the deterministic GUID
        — otherwise the script never binds at all.  Regression for the
        Breakout Brick.prefab case."""
        from src.exporter.prefab_generator import _deterministic_guid
        prefabs = tmp_path / "Assets" / "_Project" / "Prefabs"
        prefabs.mkdir(parents=True, exist_ok=True)
        (prefabs / "PlayerController.prefab").write_text(
            "%YAML 1.1\n"
            "MonoBehaviour:\n"
            "  m_Script: {fileID: 0}\n"
            "  m_Name: \n",
            encoding="utf-8",
        )
        scaffold_project("test", tmp_path, cs_files=sample_cs_files)
        healed = (prefabs / "PlayerController.prefab").read_text(encoding="utf-8")
        expected = _deterministic_guid("script:PlayerController")
        assert "{fileID: 0}" not in healed
        assert f"guid: {expected}" in healed

    def test_heal_skips_prefabs_with_multiple_scripts(self, tmp_path, sample_cs_files):
        """Multi-script prefabs can't be healed by filename alone — a
        PlayerController.prefab with scripts from other classes on its
        children would need per-component class tagging.  Skip to avoid
        rewriting the wrong script."""
        prefabs = tmp_path / "Assets" / "_Project" / "Prefabs"
        prefabs.mkdir(parents=True, exist_ok=True)
        two_scripts = (
            "%YAML 1.1\n"
            "MonoBehaviour:\n"
            "  m_Script: {fileID: 11500000, guid: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, type: 3}\n"
            "MonoBehaviour:\n"
            "  m_Script: {fileID: 11500000, guid: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb, type: 3}\n"
        )
        (prefabs / "PlayerController.prefab").write_text(two_scripts, encoding="utf-8")
        scaffold_project("test", tmp_path, cs_files=sample_cs_files)
        # Content unchanged because heal refuses to guess the mapping.
        assert "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" in (prefabs / "PlayerController.prefab").read_text(encoding="utf-8")
        assert "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" in (prefabs / "PlayerController.prefab").read_text(encoding="utf-8")
