"""Cross-system contract tests for Angry Birds — verify API and behavior contracts."""

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
from src.engine.audio import AudioSource
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


def _setup_and_start():
    """Set up level 1 and process lifecycle so start() is called."""
    from examples.angry_birds.angry_birds_python.levels import register_all_levels, setup_level_1
    from examples.angry_birds.angry_birds_python.game_manager import GameManager

    register_all_levels()
    GameManager.current_level_index = 0
    setup_level_1()

    lm = LifecycleManager.instance()
    lm.process_awake_queue()
    lm.process_start_queue()


class TestAudioSourceContracts:
    """Verify AudioSource components exist on the right objects for sound playback."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        _setup_and_start()

    def test_bird_has_audio_source(self):
        """Each bird must have an AudioSource for throw sounds."""
        birds = GameObject.find_game_objects_with_tag("Bird")
        for bird_go in birds:
            audio = bird_go.get_component(AudioSource)
            assert audio is not None, f"Bird '{bird_go.name}' missing AudioSource"

    def test_pig_has_audio_source(self):
        """Each pig must have an AudioSource for collision sounds."""
        pigs = GameObject.find_game_objects_with_tag("Pig")
        for pig_go in pigs:
            audio = pig_go.get_component(AudioSource)
            assert audio is not None, f"Pig '{pig_go.name}' missing AudioSource"

    def test_brick_has_audio_source(self):
        """Each brick must have an AudioSource for impact sounds."""
        bricks = GameObject.find_game_objects_with_tag("Brick")
        for brick_go in bricks:
            audio = brick_go.get_component(AudioSource)
            assert audio is not None, f"Brick '{brick_go.name}' missing AudioSource"

    def test_bird_on_throw_plays_audio(self):
        """Bird.on_throw() should attempt to play audio via AudioSource."""
        from examples.angry_birds.angry_birds_python.bird import Bird
        from unittest.mock import MagicMock

        bird_go = GameObject.find_game_objects_with_tag("Bird")[0]
        bird_comp = bird_go.get_component(Bird)
        audio = bird_go.get_component(AudioSource)
        audio.play = MagicMock()

        bird_comp.on_throw()
        audio.play.assert_called_once()


class TestGameManagerUISetup:
    """Verify _setup_ui creates Canvas and Text components."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        _setup_and_start()

    def test_canvas_exists(self):
        canvas_go = GameObject.find("UICanvas")
        assert canvas_go is not None, "UICanvas not created"
        canvas = canvas_go.get_component(Canvas)
        assert canvas is not None, "UICanvas missing Canvas component"

    def test_status_text_created(self):
        status_go = GameObject.find("StatusText")
        assert status_go is not None
        text = status_go.get_component(Text)
        assert text is not None

    def test_score_text_created(self):
        score_go = GameObject.find("ScoreText")
        assert score_go is not None
        text = score_go.get_component(Text)
        assert text is not None

    def test_birds_text_created(self):
        birds_go = GameObject.find("BirdsText")
        assert birds_go is not None
        text = birds_go.get_component(Text)
        assert text is not None


class TestLevelProgressionContract:
    """Verify level progression: clearing pigs loads next level when available."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        _setup_and_start()

    def test_all_pigs_destroyed_detected(self):
        """GameManager._all_pigs_destroyed() should return True when all pigs are gone."""
        from examples.angry_birds.angry_birds_python.game_manager import GameManager

        gm_go = GameObject.find("GameManager")
        gm = gm_go.get_component(GameManager)

        # Initially pigs are alive
        assert not gm._all_pigs_destroyed()

        # Destroy all pigs
        for pig in gm.pigs:
            if pig is not None and pig.active:
                GameObject.destroy(pig)

        assert gm._all_pigs_destroyed()

    def test_level_names_list_has_two_entries(self):
        """LEVEL_NAMES should contain exactly 2 levels."""
        from examples.angry_birds.angry_birds_python.game_manager import LEVEL_NAMES
        assert len(LEVEL_NAMES) == 2
        assert LEVEL_NAMES[0] == "level_1"
        assert LEVEL_NAMES[1] == "level_2"

    def test_current_level_index_starts_at_zero(self):
        from examples.angry_birds.angry_birds_python.game_manager import GameManager
        # GameManager.current_level_index is set to 0 in _setup_and_start
        assert GameManager.current_level_index == 0


class TestClassAndMethodContracts:
    """Verify Python classes have the expected method signatures matching Unity patterns."""

    def test_bird_has_required_methods(self):
        from examples.angry_birds.angry_birds_python.bird import Bird
        assert hasattr(Bird, 'start')
        assert hasattr(Bird, 'fixed_update')
        assert hasattr(Bird, 'on_throw')
        assert hasattr(Bird, '_destroy_after')

    def test_slingshot_has_required_methods(self):
        from examples.angry_birds.angry_birds_python.slingshot import Slingshot
        assert hasattr(Slingshot, 'start')
        assert hasattr(Slingshot, 'update')
        assert hasattr(Slingshot, '_handle_idle')
        assert hasattr(Slingshot, '_handle_pulling')
        assert hasattr(Slingshot, '_throw_bird')

    def test_brick_has_required_methods(self):
        from examples.angry_birds.angry_birds_python.brick import Brick
        assert hasattr(Brick, 'on_collision_enter_2d')
        assert hasattr(Brick, '_update_color')

    def test_pig_has_required_methods(self):
        from examples.angry_birds.angry_birds_python.pig import Pig
        assert hasattr(Pig, 'on_collision_enter_2d')
        assert hasattr(Pig, '_play_sound')
        assert hasattr(Pig, '_show_hurt')

    def test_game_manager_has_required_methods(self):
        from examples.angry_birds.angry_birds_python.game_manager import GameManager
        assert hasattr(GameManager, 'start')
        assert hasattr(GameManager, 'update')
        assert hasattr(GameManager, '_setup_ui')
        assert hasattr(GameManager, '_handle_start')
        assert hasattr(GameManager, '_handle_playing')
        assert hasattr(GameManager, '_next_turn')
        assert hasattr(GameManager, '_load_next_bird')
        assert hasattr(GameManager, '_all_pigs_destroyed')
        assert hasattr(GameManager, '_all_stopped')

    def test_destroyer_has_on_trigger_enter_2d(self):
        from examples.angry_birds.angry_birds_python.destroyer import Destroyer
        assert hasattr(Destroyer, 'on_trigger_enter_2d')

    def test_constants_match_expected_values(self):
        """Key constants should have specific values for game balance."""
        from examples.angry_birds.angry_birds_python.constants import Constants
        assert Constants.THROW_SPEED == 5.0
        assert Constants.SLINGSHOT_MAX_PULL == 1.5
        assert Constants.BIRD_DESTROY_DELAY == 2.0
        assert Constants.SETTLE_TIMEOUT == 5.0
        assert Constants.TRAJECTORY_SEGMENTS == 15

    def test_enums_match_expected_values(self):
        from examples.angry_birds.angry_birds_python.enums import GameState, SlingshotState, BirdState
        assert GameState.START.value == "start"
        assert GameState.PLAYING.value == "playing"
        assert GameState.WON.value == "won"
        assert GameState.LOST.value == "lost"
        assert SlingshotState.IDLE.value == "idle"
        assert SlingshotState.BIRD_FLYING.value == "bird_flying"
        assert BirdState.BEFORE_THROWN.value == "before_thrown"
        assert BirdState.THROWN.value == "thrown"
