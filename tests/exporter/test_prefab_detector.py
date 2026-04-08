"""Tests for prefab_detector — classifies GameObjects as prefabs vs scene objects."""

import pytest
from src.exporter.prefab_detector import detect_prefabs


class TestBreakoutDetection:
    """Breakout: bricks in loops = prefabs, paddle/ball/walls = scene objects."""

    @pytest.fixture(autouse=True)
    def detect(self):
        self.result = detect_prefabs("examples/breakout")
        self.prefab_names = [p["class_name"] for p in self.result["prefabs"]]
        self.scene_names = [s["name"] for s in self.result["scene_objects"]]

    def test_returns_prefabs_and_scene_objects_keys(self):
        assert "prefabs" in self.result
        assert "scene_objects" in self.result

    def test_bricks_are_prefabs(self):
        # Bricks are created in a nested for loop — classic prefab pattern
        assert any("Brick" in name for name in self.prefab_names), (
            f"Expected 'Brick' in prefabs, got: {self.prefab_names}"
        )

    def test_paddle_is_scene_object(self):
        assert any("Paddle" in name for name in self.scene_names), (
            f"Expected 'Paddle' in scene objects, got: {self.scene_names}"
        )

    def test_ball_is_scene_object(self):
        assert any("Ball" in name for name in self.scene_names), (
            f"Expected 'Ball' in scene objects, got: {self.scene_names}"
        )

    def test_prefab_entries_have_class_name(self):
        for prefab in self.result["prefabs"]:
            assert "class_name" in prefab, f"Prefab missing 'class_name': {prefab}"

    def test_prefab_entries_have_components(self):
        for prefab in self.result["prefabs"]:
            assert "components" in prefab, f"Prefab missing 'components': {prefab}"
            assert isinstance(prefab["components"], list)

    def test_brick_prefab_has_expected_components(self):
        brick_prefabs = [p for p in self.result["prefabs"] if "Brick" in p["class_name"]]
        assert len(brick_prefabs) > 0
        brick = brick_prefabs[0]
        # Bricks have Rigidbody2D, BoxCollider2D, SpriteRenderer, AudioSource, Brick
        assert "Rigidbody2D" in brick["components"]
        assert "BoxCollider2D" in brick["components"]
        assert "SpriteRenderer" in brick["components"]
        assert "Brick" in brick["components"]

    def test_scene_objects_not_in_prefabs(self):
        # Paddle and Ball should NOT appear in the prefab list
        for prefab in self.result["prefabs"]:
            assert "Paddle" not in prefab["class_name"]
            assert "Ball" not in prefab["class_name"]


class TestPacmanDetection:
    """Pacman: pellets/walls in loops = prefabs, pacman/ghosts = scene objects."""

    @pytest.fixture(autouse=True)
    def detect(self):
        self.result = detect_prefabs("examples/pacman_v2")
        self.prefab_names = [p["class_name"] for p in self.result["prefabs"]]
        self.scene_names = [s["name"] for s in self.result["scene_objects"]]

    def test_pellets_are_prefabs(self):
        assert any("Pellet" in name for name in self.prefab_names), (
            f"Expected 'Pellet' in prefabs, got: {self.prefab_names}"
        )

    def test_walls_are_prefabs(self):
        assert any("Wall" in name for name in self.prefab_names), (
            f"Expected 'Wall' in prefabs, got: {self.prefab_names}"
        )

    def test_pacman_is_scene_object(self):
        # Pacman is created individually (not in a generic loop)
        assert any("Pacman" in name or "pacman" in name for name in self.scene_names), (
            f"Expected 'Pacman' in scene objects, got: {self.scene_names}"
        )

    def test_camera_is_scene_object(self):
        assert any("Camera" in name or "MainCamera" in name for name in self.scene_names), (
            f"Expected camera in scene objects, got: {self.scene_names}"
        )

    def test_ghost_loop_creates_prefabs(self):
        # Ghosts are created in a for loop iterating ghost_configs
        assert any("Ghost" in name for name in self.prefab_names), (
            f"Expected 'Ghost' in prefabs, got: {self.prefab_names}"
        )


class TestEmptyDirectory:
    """Edge case: directory with no Python files or no GameObjects."""

    def test_empty_returns_empty_lists(self, tmp_path):
        result = detect_prefabs(str(tmp_path))
        assert result == {"prefabs": [], "scene_objects": []}

    def test_no_gameobjects_returns_empty(self, tmp_path):
        (tmp_path / "empty.py").write_text("x = 1\n")
        result = detect_prefabs(str(tmp_path))
        assert result == {"prefabs": [], "scene_objects": []}
