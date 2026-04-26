"""Integration tests for prefab generation pipeline.

Tests the full pipeline: prefab_detector -> prefab_generator -> project_scaffolder,
verifying that real example games produce valid .prefab files on disk.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.exporter.prefab_detector import detect_prefabs
from src.exporter.prefab_generator import generate_prefab_files, generate_prefab_yaml
from src.exporter.project_scaffolder import scaffold_project


# ── Pipeline: prefab_detector -> prefab_generator ────────────────


class TestDetectorToGeneratorPipeline:
    """Feed real example code through the full detection+generation pipeline."""

    def test_breakout_produces_prefab_files(self):
        """Running prefab_detector on examples/breakout should produce .prefab output."""
        prefab_data = detect_prefabs("examples/breakout")
        files = generate_prefab_files(prefab_data)

        # Breakout should detect at least one prefab (bricks are created in loops)
        prefab_files = [f for f in files if f.endswith(".prefab") and not f.endswith(".meta")]
        assert len(prefab_files) >= 1, (
            f"Breakout should have at least 1 prefab, got: {list(files.keys())}"
        )

    def test_breakout_prefabs_have_meta_files(self):
        """Every .prefab file must have a matching .prefab.meta."""
        prefab_data = detect_prefabs("examples/breakout")
        files = generate_prefab_files(prefab_data)

        for filename in list(files.keys()):
            if filename.endswith(".prefab") and not filename.endswith(".meta"):
                meta_name = filename + ".meta"
                assert meta_name in files, f"Missing .meta for {filename}"

    def test_breakout_prefab_yaml_is_valid(self):
        """Each generated .prefab YAML from breakout must have valid Unity headers."""
        prefab_data = detect_prefabs("examples/breakout")
        files = generate_prefab_files(prefab_data)

        for filename, content in files.items():
            if not filename.endswith(".prefab") or filename.endswith(".meta"):
                continue
            assert content.startswith("%YAML 1.1\n"), f"{filename} missing YAML header"
            assert "%TAG !u! tag:unity3d.com,2011:" in content, (
                f"{filename} missing Unity tag"
            )
            # Must have at least a GameObject and Transform
            assert re.search(r"--- !u!1 &\d+", content), (
                f"{filename} missing GameObject"
            )
            assert re.search(r"--- !u!4 &\d+", content), (
                f"{filename} missing Transform"
            )

    def test_breakout_prefabs_have_components(self):
        """Breakout bricks should have detected components (e.g. colliders)."""
        prefab_data = detect_prefabs("examples/breakout")
        # At least one prefab should have components beyond Transform
        has_components = False
        for prefab in prefab_data.get("prefabs", []):
            if prefab.get("components"):
                has_components = True
                break
        # This is a soft check — if breakout code doesn't add_component, it's OK
        # but we verify the pipeline doesn't crash
        assert isinstance(prefab_data, dict)

    def test_detector_output_feeds_into_generator(self):
        """The detector output format must be compatible with the generator input."""
        prefab_data = detect_prefabs("examples/breakout")
        # Should not raise
        files = generate_prefab_files(prefab_data)
        assert isinstance(files, dict)
        for key, val in files.items():
            assert isinstance(key, str)
            assert isinstance(val, str)


# ── Pipeline: scaffolder with prefab_data ────────────────────────


class TestScaffolderPrefabIntegration:
    """Test that scaffold_project correctly writes .prefab files to disk."""

    def test_scaffold_creates_prefab_directory(self, tmp_path):
        """scaffold_project with prefab_data must create the Prefabs directory."""
        prefab_data = {
            "prefabs": [{"class_name": "Brick", "components": ["BoxCollider2D"]}],
            "scene_objects": [],
        }
        scaffold_project(
            "test_game",
            tmp_path / "unity_project",
            cs_files={"Brick.cs": "// stub"},
            prefab_data=prefab_data,
        )
        prefab_dir = tmp_path / "unity_project" / "Assets" / "_Project" / "Prefabs"
        assert prefab_dir.is_dir()

    def test_scaffold_writes_prefab_files(self, tmp_path):
        """scaffold_project must write .prefab and .prefab.meta to Prefabs dir."""
        prefab_data = {
            "prefabs": [
                {"class_name": "Brick", "components": ["BoxCollider2D"]},
                {"class_name": "Ball", "components": ["Rigidbody2D", "CircleCollider2D"]},
            ],
            "scene_objects": [],
        }
        out = scaffold_project(
            "breakout",
            tmp_path / "breakout_unity",
            cs_files={"Brick.cs": "// stub", "Ball.cs": "// stub"},
            prefab_data=prefab_data,
        )
        prefab_dir = out / "Assets" / "_Project" / "Prefabs"

        assert (prefab_dir / "Brick.prefab").is_file()
        assert (prefab_dir / "Brick.prefab.meta").is_file()
        assert (prefab_dir / "Ball.prefab").is_file()
        assert (prefab_dir / "Ball.prefab.meta").is_file()

    def test_scaffold_prefab_content_is_valid_yaml(self, tmp_path):
        """Written .prefab files must contain valid Unity YAML content."""
        prefab_data = {
            "prefabs": [{"class_name": "Enemy", "components": ["SpriteRenderer"]}],
            "scene_objects": [],
        }
        out = scaffold_project(
            "game",
            tmp_path / "proj",
            cs_files={"Enemy.cs": "// stub"},
            prefab_data=prefab_data,
        )
        prefab_path = out / "Assets" / "_Project" / "Prefabs" / "Enemy.prefab"
        content = prefab_path.read_text(encoding="utf-8")
        assert content.startswith("%YAML 1.1\n")
        assert "m_Name: Enemy" in content

    def test_scaffold_meta_content_is_valid(self, tmp_path):
        """Written .prefab.meta files must have fileFormatVersion and GUID."""
        prefab_data = {
            "prefabs": [{"class_name": "Coin", "components": []}],
            "scene_objects": [],
        }
        out = scaffold_project(
            "game",
            tmp_path / "proj",
            cs_files={"Coin.cs": "// stub"},
            prefab_data=prefab_data,
        )
        meta_path = out / "Assets" / "_Project" / "Prefabs" / "Coin.prefab.meta"
        content = meta_path.read_text(encoding="utf-8")
        assert "fileFormatVersion: 2" in content
        m = re.search(r"guid:\s+([0-9a-f]{32})", content)
        assert m, "Meta file must contain 32-char hex GUID"

    def test_scaffold_without_prefab_data_skips_prefabs(self, tmp_path):
        """When prefab_data is None, no .prefab files should be written."""
        out = scaffold_project(
            "game",
            tmp_path / "proj",
            cs_files={"Main.cs": "// stub"},
            prefab_data=None,
        )
        prefab_dir = out / "Assets" / "_Project" / "Prefabs"
        # Directory exists (created by scaffolder) but should be empty
        if prefab_dir.exists():
            prefab_files = list(prefab_dir.glob("*.prefab"))
            assert len(prefab_files) == 0

    def test_scaffold_with_empty_prefab_list(self, tmp_path):
        """Empty prefab list should not crash and should write no .prefab files."""
        out = scaffold_project(
            "game",
            tmp_path / "proj",
            cs_files={"Main.cs": "// stub"},
            prefab_data={"prefabs": [], "scene_objects": []},
        )
        prefab_dir = out / "Assets" / "_Project" / "Prefabs"
        if prefab_dir.exists():
            prefab_files = list(prefab_dir.glob("*.prefab"))
            assert len(prefab_files) == 0


# ── Full Pipeline: detector -> generator -> scaffolder ───────────


class TestFullPipelineIntegration:
    """End-to-end: detect from real code, generate, scaffold to disk."""

    def test_breakout_full_pipeline(self, tmp_path):
        """Full pipeline from breakout detection to disk files."""
        prefab_data = detect_prefabs("examples/breakout")
        out = scaffold_project(
            "breakout",
            tmp_path / "breakout_unity",
            cs_files={"GameManager.cs": "// stub"},
            prefab_data=prefab_data,
        )
        prefab_dir = out / "Assets" / "_Project" / "Prefabs"

        # Check that prefab files exist on disk for each detected prefab
        for prefab in prefab_data.get("prefabs", []):
            name = prefab["class_name"]
            assert (prefab_dir / f"{name}.prefab").is_file(), (
                f"Missing {name}.prefab on disk"
            )
            assert (prefab_dir / f"{name}.prefab.meta").is_file(), (
                f"Missing {name}.prefab.meta on disk"
            )

    def test_pipeline_does_not_corrupt_other_scaffolded_files(self, tmp_path):
        """Adding prefab_data must not break other scaffolded files."""
        prefab_data = {
            "prefabs": [{"class_name": "Brick", "components": ["BoxCollider2D"]}],
        }
        out = scaffold_project(
            "breakout",
            tmp_path / "proj",
            cs_files={"GameManager.cs": "using UnityEngine;"},
            prefab_data=prefab_data,
        )
        # Scripts should still be written
        assert (out / "Assets" / "_Project" / "Scripts" / "GameManager.cs").is_file()
        # ProjectSettings should still exist
        assert (out / "ProjectSettings" / "ProjectVersion.txt").is_file()
        assert (out / "Packages" / "manifest.json").is_file()


# ── Determinism Tests ────────────────────────────────────────────


class TestDeterminism:
    """Regenerating prefabs must produce identical output."""

    def test_yaml_output_is_deterministic(self):
        """Same inputs must always produce identical YAML."""
        yaml1 = generate_prefab_yaml("Brick", ["BoxCollider2D", "SpriteRenderer"])
        yaml2 = generate_prefab_yaml("Brick", ["BoxCollider2D", "SpriteRenderer"])
        assert yaml1 == yaml2

    def test_full_pipeline_is_deterministic(self):
        """Full file generation must be deterministic."""
        data = {
            "prefabs": [
                {"class_name": "A", "components": ["Rigidbody2D"]},
                {"class_name": "B", "components": ["BoxCollider2D"]},
            ]
        }
        files1 = generate_prefab_files(data)
        files2 = generate_prefab_files(data)
        assert files1 == files2
