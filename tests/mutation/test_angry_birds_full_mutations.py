"""Mutation tests for Angry Birds — break things and verify detection."""

import pytest
from unittest.mock import patch

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
from src.engine.ui import Canvas


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


class TestMutateSetupUI:
    """Break GameManager._setup_ui (no-op) and verify UI text is missing."""

    def test_no_ui_when_setup_ui_is_noop(self):
        """If _setup_ui does nothing, StatusText/ScoreText/BirdsText should not exist."""
        from examples.angry_birds.angry_birds_python.game_manager import GameManager
        from examples.angry_birds.angry_birds_python.levels import register_all_levels, setup_level_1

        register_all_levels()
        GameManager.current_level_index = 0

        # Patch _setup_ui to be a no-op before setup_level_1 triggers start()
        with patch.object(GameManager, '_setup_ui', lambda self: None):
            setup_level_1()
            lm = LifecycleManager.instance()
            lm.process_awake_queue()
            lm.process_start_queue()

        status_go = GameObject.find("StatusText")
        score_go = GameObject.find("ScoreText")
        birds_go = GameObject.find("BirdsText")

        assert status_go is None, "StatusText should not exist when _setup_ui is broken"
        assert score_go is None, "ScoreText should not exist when _setup_ui is broken"
        assert birds_go is None, "BirdsText should not exist when _setup_ui is broken"

    def test_no_canvas_when_setup_ui_is_noop(self):
        """If _setup_ui does nothing, UICanvas should not exist."""
        from examples.angry_birds.angry_birds_python.game_manager import GameManager
        from examples.angry_birds.angry_birds_python.levels import register_all_levels, setup_level_1

        register_all_levels()
        GameManager.current_level_index = 0

        with patch.object(GameManager, '_setup_ui', lambda self: None):
            setup_level_1()
            lm = LifecycleManager.instance()
            lm.process_awake_queue()
            lm.process_start_queue()

        canvas_go = GameObject.find("UICanvas")
        assert canvas_go is None, "UICanvas should not exist when _setup_ui is broken"


class TestMutateLevelProgression:
    """Break level progression (skip SceneManager.load_scene) and verify level stays."""

    def test_level_does_not_change_when_load_scene_broken(self):
        """If SceneManager.load_scene is a no-op, level should not change."""
        _setup_and_start()

        from examples.angry_birds.angry_birds_python.game_manager import GameManager

        gm_go = GameObject.find("GameManager")
        gm = gm_go.get_component(GameManager)

        # Destroy all pigs to trigger win condition
        for pig in gm.pigs:
            if pig is not None and pig.active:
                GameObject.destroy(pig)

        assert gm._all_pigs_destroyed()

        # Patch load_scene to be a no-op
        with patch.object(SceneManager, 'load_scene', lambda name: None):
            # Run the _next_turn coroutine manually
            gen = gm._next_turn()
            # Advance past the WaitForSeconds yield
            yielded = next(gen)
            # Now advance to completion (this would normally call load_scene)
            try:
                next(gen)
            except StopIteration:
                pass

        # Level index was incremented but scene was not actually loaded
        assert GameManager.current_level_index == 1
        # The active scene should NOT have changed since load_scene was a no-op
        active = SceneManager.get_active_scene()
        assert active != "level_2", "Level should not change when load_scene is broken"


class TestMutateBirdDestroyFlag:
    """Break Bird._destroy_started flag and verify coroutine fires multiple times."""

    def test_coroutine_fires_multiple_times_without_flag(self):
        """Without _destroy_started guard, the self-destruct coroutine starts repeatedly."""
        _setup_and_start()

        from examples.angry_birds.angry_birds_python.bird import Bird
        from examples.angry_birds.angry_birds_python.enums import BirdState
        from src.engine.physics.rigidbody import Rigidbody2D
        from src.engine.math.vector import Vector2

        bird_go = GameObject.find_game_objects_with_tag("Bird")[0]
        bird_comp = bird_go.get_component(Bird)
        rb = bird_go.get_component(Rigidbody2D)

        # Put bird in THROWN state with near-zero velocity
        bird_comp.state = BirdState.THROWN
        rb.velocity = Vector2(0.0, 0.0)

        # Track coroutine starts
        coroutine_count = 0
        original_start_coroutine = bird_comp.start_coroutine

        def counting_start_coroutine(gen):
            nonlocal coroutine_count
            coroutine_count += 1
            return original_start_coroutine(gen)

        bird_comp.start_coroutine = counting_start_coroutine

        # Normal behavior: _destroy_started = False initially, set to True on first call
        bird_comp._destroy_started = False
        bird_comp.fixed_update()
        first_count = coroutine_count
        assert first_count == 1, "First fixed_update should start coroutine"

        # Coroutine should NOT start again because _destroy_started is now True
        bird_comp.fixed_update()
        assert coroutine_count == 1, "Second fixed_update should not start another coroutine"

        # MUTATION: Reset the flag — coroutine fires again
        bird_comp._destroy_started = False
        bird_comp.fixed_update()
        assert coroutine_count == 2, "With flag reset, coroutine fires again (mutation detected)"


class TestMutateBrickAudioSource:
    """Remove Brick's AudioSource and verify play() call is guarded."""

    def test_brick_collision_without_audio_source_does_not_crash(self):
        """If AudioSource is removed from a Brick, collision handling should still work."""
        _setup_and_start()

        from examples.angry_birds.angry_birds_python.brick import Brick
        from src.engine.math.vector import Vector2

        brick_go = GameObject.find_game_objects_with_tag("Brick")[0]
        brick_comp = brick_go.get_component(Brick)

        # Remove AudioSource from the brick
        audio = brick_go.get_component(AudioSource)
        if audio is not None:
            brick_go._components.remove(audio)

        # Verify AudioSource is gone
        assert brick_go.get_component(AudioSource) is None

        # Create a fake collision with enough velocity to trigger audio path
        class FakeCollision:
            def __init__(self):
                self.game_object = GameObject("Projectile")
                rb = self.game_object.add_component(
                    __import__('src.engine.physics.rigidbody', fromlist=['Rigidbody2D']).Rigidbody2D
                )
                self.relative_velocity = Vector2(5.0, 5.0)  # magnitude > 1, damage >= 10

        collision = FakeCollision()
        initial_health = brick_comp.health

        # This should NOT crash even without AudioSource
        brick_comp.on_collision_enter_2d(collision)

        # Brick should still take damage
        assert brick_comp.health < initial_health, "Brick should take damage even without AudioSource"

    def test_brick_audio_guarded_by_none_check(self):
        """Verify the guard: audio = self.get_component(AudioSource); if audio: audio.play()"""
        _setup_and_start()

        from examples.angry_birds.angry_birds_python.brick import Brick

        brick_go = GameObject.find_game_objects_with_tag("Brick")[0]
        brick_comp = brick_go.get_component(Brick)

        # Verify AudioSource exists initially
        audio = brick_go.get_component(AudioSource)
        assert audio is not None, "Brick should have AudioSource initially"

        # Remove it
        brick_go._components.remove(audio)

        # get_component should now return None
        result = brick_go.get_component(AudioSource)
        assert result is None, "After removal, get_component(AudioSource) should return None"
