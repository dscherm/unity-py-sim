"""Tests for Physics2DSettings.asset generation in the project scaffolder.

Verifies that scaffold_project() can accept physics configuration and generate
a valid ProjectSettings/Physics2DSettings.asset in Unity YAML format.
"""

from __future__ import annotations


import pytest

from src.exporter.project_scaffolder import scaffold_project


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_cs_files() -> dict[str, str]:
    return {
        "GameManager.cs": "using UnityEngine;\npublic class GameManager : MonoBehaviour { }\n",
    }


@pytest.fixture
def physics_config() -> dict:
    return {
        "gravity": [0, 0],
        "ignore_pairs": [["Ghost", "Ghost"], ["Ghost", "Pellet"]],
    }


# ---------------------------------------------------------------------------
# Physics2DSettings.asset existence
# ---------------------------------------------------------------------------

class TestPhysics2DSettingsExistence:

    def test_physics_settings_created_when_physics_provided(
        self, tmp_path, minimal_cs_files, physics_config
    ):
        scaffold_project("pacman", tmp_path, cs_files=minimal_cs_files, physics=physics_config)
        ps = tmp_path / "ProjectSettings" / "Physics2DSettings.asset"
        assert ps.is_file(), "Physics2DSettings.asset must exist when physics config provided"

    def test_physics_settings_created_with_defaults_when_no_physics(
        self, tmp_path, minimal_cs_files
    ):
        """Even without explicit physics, a default Physics2DSettings.asset should be generated."""
        scaffold_project("pacman", tmp_path, cs_files=minimal_cs_files)
        ps = tmp_path / "ProjectSettings" / "Physics2DSettings.asset"
        assert ps.is_file(), "Physics2DSettings.asset must exist even without physics arg"


# ---------------------------------------------------------------------------
# YAML header
# ---------------------------------------------------------------------------

class TestPhysics2DSettingsFormat:

    def test_starts_with_yaml_header(self, tmp_path, minimal_cs_files, physics_config):
        scaffold_project("pacman", tmp_path, cs_files=minimal_cs_files, physics=physics_config)
        content = (tmp_path / "ProjectSettings" / "Physics2DSettings.asset").read_text()
        assert content.startswith("%YAML 1.1"), "Must start with %YAML 1.1 header"

    def test_contains_unity_tag(self, tmp_path, minimal_cs_files, physics_config):
        scaffold_project("pacman", tmp_path, cs_files=minimal_cs_files, physics=physics_config)
        content = (tmp_path / "ProjectSettings" / "Physics2DSettings.asset").read_text()
        assert "%TAG !u! tag:unity3d.com,2011:" in content


# ---------------------------------------------------------------------------
# Gravity values
# ---------------------------------------------------------------------------

class TestGravityValues:

    def test_custom_gravity_present(self, tmp_path, minimal_cs_files):
        physics = {"gravity": [0, 0], "ignore_pairs": []}
        scaffold_project("pacman", tmp_path, cs_files=minimal_cs_files, physics=physics)
        content = (tmp_path / "ProjectSettings" / "Physics2DSettings.asset").read_text()
        assert "x: 0" in content
        assert "y: 0" in content

    def test_default_gravity_when_no_physics(self, tmp_path, minimal_cs_files):
        scaffold_project("pacman", tmp_path, cs_files=minimal_cs_files)
        content = (tmp_path / "ProjectSettings" / "Physics2DSettings.asset").read_text()
        # Default Unity 2D gravity is (0, -9.81)
        assert "x: 0" in content
        assert "y: -9.81" in content

    def test_nonstandard_gravity(self, tmp_path, minimal_cs_files):
        physics = {"gravity": [1.5, -20.0], "ignore_pairs": []}
        scaffold_project("pacman", tmp_path, cs_files=minimal_cs_files, physics=physics)
        content = (tmp_path / "ProjectSettings" / "Physics2DSettings.asset").read_text()
        assert "x: 1.5" in content
        assert "y: -20.0" in content


# ---------------------------------------------------------------------------
# Layer collision matrix
# ---------------------------------------------------------------------------

class TestLayerCollisionMatrix:

    def test_collision_matrix_present(self, tmp_path, minimal_cs_files, physics_config):
        scaffold_project("pacman", tmp_path, cs_files=minimal_cs_files, physics=physics_config)
        content = (tmp_path / "ProjectSettings" / "Physics2DSettings.asset").read_text()
        assert "m_LayerCollisionMatrix" in content

    def test_default_matrix_all_collide(self, tmp_path, minimal_cs_files):
        """With no ignore pairs, all 32 layers should collide with all others (0xFFFFFFFF)."""
        scaffold_project("pacman", tmp_path, cs_files=minimal_cs_files)
        content = (tmp_path / "ProjectSettings" / "Physics2DSettings.asset").read_text()
        # All-collide = 4294967295 (0xFFFFFFFF) for each layer row
        assert "4294967295" in content
