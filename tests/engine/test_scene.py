"""Tests for SceneManager — scene registration, loading, persistence."""

import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.scene import SceneManager, dont_destroy_on_load


@pytest.fixture(autouse=True)
def reset():
    yield
    SceneManager.clear()


class TestSceneManager:
    def test_register_scene(self):
        SceneManager.register_scene("menu", lambda: None)
        assert SceneManager.get_scene_count() == 1

    def test_load_scene_by_name(self):
        setup_called = [False]

        def menu_setup():
            setup_called[0] = True
            GameObject("MenuButton")

        SceneManager.register_scene("menu", menu_setup)
        SceneManager.load_scene("menu")
        assert setup_called[0]
        assert SceneManager.get_active_scene() == "menu"
        assert GameObject.find("MenuButton") is not None

    def test_load_scene_by_index(self):
        SceneManager.register_scene("menu", lambda: GameObject("Menu"))
        SceneManager.register_scene("game", lambda: GameObject("Game"))
        SceneManager.load_scene(1)
        assert SceneManager.get_active_scene() == "game"
        assert GameObject.find("Game") is not None

    def test_load_scene_clears_old_objects(self):
        go = GameObject("OldObject")
        assert GameObject.find("OldObject") is not None

        SceneManager.register_scene("new", lambda: GameObject("NewObject"))
        SceneManager.load_scene("new")
        assert GameObject.find("OldObject") is None
        assert GameObject.find("NewObject") is not None

    def test_load_scene_invalid_name(self):
        with pytest.raises(ValueError):
            SceneManager.load_scene("nonexistent")

    def test_load_scene_invalid_index(self):
        with pytest.raises(ValueError):
            SceneManager.load_scene(99)

    def test_get_active_scene_default(self):
        assert SceneManager.get_active_scene() is None


class TestDontDestroyOnLoad:
    def test_persistent_object_survives_scene_load(self):
        persistent = GameObject("GameManager")
        dont_destroy_on_load(persistent)
        temporary = GameObject("Enemy")

        SceneManager.register_scene("level2", lambda: GameObject("NewEnemy"))
        SceneManager.load_scene("level2")

        assert GameObject.find("GameManager") is not None
        assert GameObject.find("Enemy") is None
        assert GameObject.find("NewEnemy") is not None

    def test_non_persistent_destroyed(self):
        go = GameObject("Temp")
        SceneManager.register_scene("next", lambda: None)
        SceneManager.load_scene("next")
        assert GameObject.find("Temp") is None

    def test_multiple_persistent_objects(self):
        gm = GameObject("GM")
        audio = GameObject("AudioMgr")
        dont_destroy_on_load(gm)
        dont_destroy_on_load(audio)
        temp = GameObject("Temp")

        SceneManager.register_scene("s2", lambda: None)
        SceneManager.load_scene("s2")

        assert GameObject.find("GM") is not None
        assert GameObject.find("AudioMgr") is not None
        assert GameObject.find("Temp") is None
