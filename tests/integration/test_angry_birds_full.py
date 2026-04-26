"""Full integration tests for Angry Birds — runs through app.run() headless."""

import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.rendering.camera import Camera
from src.engine.rendering.display import DisplayManager
from src.engine.input_manager import Input
from src.engine.time_manager import Time
from src.engine.debug import Debug
from src.engine.scene import SceneManager
from src.engine.ui import Canvas, Text


@pytest.fixture(autouse=True)
def _reset_all():
    """Reset all singletons before and after each test."""
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    DisplayManager.reset()
    SceneManager.clear()
    Canvas.reset()
    Camera.main = None
    Input._reset()
    Time._reset()
    Debug._reset()
    yield
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    DisplayManager.reset()
    SceneManager.clear()
    Canvas.reset()
    Camera.main = None
    Input._reset()
    Time._reset()
    Debug._reset()


def _run_angry_birds_headless(max_frames=500):
    """Run the Angry Birds game headless for a given number of frames."""
    import sys
    import os
    # Ensure examples directory is on the path
    examples_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "examples", "angry_birds"
    )
    if examples_dir not in sys.path:
        sys.path.insert(0, os.path.abspath(examples_dir))

    from examples.angry_birds.angry_birds_python.levels import register_all_levels, setup_level_1
    from examples.angry_birds.angry_birds_python.game_manager import GameManager
    from src.engine.app import run

    def setup_scene():
        register_all_levels()
        GameManager.current_level_index = 0
        setup_level_1()

    run(setup_scene, width=900, height=600, headless=True, max_frames=max_frames,
        title="Angry Birds Test")


class TestFullSceneRun:
    """Verify the complete game loads and runs without crashing."""

    def test_full_scene_runs_500_frames_without_crash(self):
        """The game should survive 500 headless frames without any exception."""
        _run_angry_birds_headless(max_frames=500)

    def test_full_scene_runs_100_frames_without_crash(self):
        """Shorter run to confirm basic stability."""
        _run_angry_birds_headless(max_frames=100)


class TestExpectedObjectsExist:
    """After setup_level_1, verify all expected GameObjects are present."""

    @pytest.fixture(autouse=True)
    def _setup_level(self):
        from examples.angry_birds.angry_birds_python.levels import register_all_levels, setup_level_1
        from examples.angry_birds.angry_birds_python.game_manager import GameManager

        register_all_levels()
        GameManager.current_level_index = 0
        setup_level_1()

        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

    def test_three_birds_exist(self):
        birds = GameObject.find_game_objects_with_tag("Bird")
        assert len(birds) == 3, f"Expected 3 birds, found {len(birds)}"

    def test_two_pigs_exist(self):
        pigs = GameObject.find_game_objects_with_tag("Pig")
        assert len(pigs) == 2, f"Expected 2 pigs, found {len(pigs)}"

    def test_six_bricks_exist(self):
        bricks = GameObject.find_game_objects_with_tag("Brick")
        assert len(bricks) == 6, f"Expected 6 bricks, found {len(bricks)}"

    def test_slingshot_exists(self):
        sling = GameObject.find("Slingshot")
        assert sling is not None, "Slingshot not found"

    def test_ground_exists(self):
        ground = GameObject.find("Ground")
        assert ground is not None, "Ground not found"

    def test_destroyers_exist(self):
        bottom = GameObject.find("Destroyer_Bottom")
        left = GameObject.find("Destroyer_Left")
        right = GameObject.find("Destroyer_Right")
        assert bottom is not None, "Destroyer_Bottom not found"
        assert left is not None, "Destroyer_Left not found"
        assert right is not None, "Destroyer_Right not found"

    def test_main_camera_exists(self):
        cam = GameObject.find("MainCamera")
        assert cam is not None, "MainCamera not found"


class TestGameManagerState:
    """Verify GameManager initial state and UI elements."""

    @pytest.fixture(autouse=True)
    def _setup_level(self):
        from examples.angry_birds.angry_birds_python.levels import register_all_levels, setup_level_1
        from examples.angry_birds.angry_birds_python.game_manager import GameManager

        register_all_levels()
        GameManager.current_level_index = 0
        setup_level_1()

        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

    def test_game_manager_starts_in_start_state(self):
        from examples.angry_birds.angry_birds_python.game_manager import GameManager
        from examples.angry_birds.angry_birds_python.enums import GameState

        gm_go = GameObject.find("GameManager")
        assert gm_go is not None, "GameManager GameObject not found"
        gm = gm_go.get_component(GameManager)
        assert gm is not None, "GameManager component not found"
        assert gm.game_state == GameState.START

    def test_status_text_exists(self):
        status_go = GameObject.find("StatusText")
        assert status_go is not None, "StatusText not found"
        text = status_go.get_component(Text)
        assert text is not None, "StatusText has no Text component"
        assert text.text == "Click to Start"

    def test_score_text_exists(self):
        score_go = GameObject.find("ScoreText")
        assert score_go is not None, "ScoreText not found"
        text = score_go.get_component(Text)
        assert text is not None, "ScoreText has no Text component"
        assert "Score" in text.text

    def test_birds_text_exists(self):
        birds_go = GameObject.find("BirdsText")
        assert birds_go is not None, "BirdsText not found"
        text = birds_go.get_component(Text)
        assert text is not None, "BirdsText has no Text component"

    def test_ui_text_updates_after_frame(self):
        """After an update tick, BirdsText should reflect remaining birds."""
        from examples.angry_birds.angry_birds_python.game_manager import GameManager

        gm_go = GameObject.find("GameManager")
        gm = gm_go.get_component(GameManager)

        Time._delta_time = 0.016
        Time._time += 0.016
        lm = LifecycleManager.instance()
        lm.run_update()

        birds_go = GameObject.find("BirdsText")
        text = birds_go.get_component(Text)
        assert "Birds" in text.text


class TestLevel2Registration:
    """Verify level 2 exists in the SceneManager registry."""

    @pytest.fixture(autouse=True)
    def _setup_levels(self):
        from examples.angry_birds.angry_birds_python.levels import register_all_levels
        register_all_levels()

    def test_level_2_registered(self):
        assert SceneManager.get_scene_count() >= 2, "Expected at least 2 scenes registered"

    def test_level_2_in_scenes(self):
        assert "level_2" in SceneManager._scenes, "level_2 not registered in SceneManager"

    def test_level_1_in_scenes(self):
        assert "level_1" in SceneManager._scenes, "level_1 not registered in SceneManager"
