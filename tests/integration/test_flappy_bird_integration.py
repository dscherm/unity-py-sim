"""Integration tests for Flappy Bird — run through the actual game setup and lifecycle."""

import pytest

from src.engine.core import MonoBehaviour, GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.time_manager import Time
from src.engine.rendering.camera import Camera
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D
from src.engine.math.vector import Vector2, Vector3
from src.engine.math.quaternion import Quaternion
from src.engine.ui import Canvas, RectTransform, Text, TextAnchor

from examples.flappy_bird.flappy_bird_python.player import Player
from examples.flappy_bird.flappy_bird_python.game_manager import GameManager
from examples.flappy_bird.flappy_bird_python.pipes import Pipes
from examples.flappy_bird.flappy_bird_python.spawner import Spawner
from examples.flappy_bird.flappy_bird_python.parallax import Parallax


@pytest.fixture(autouse=True)
def clean_state():
    """Reset all global state between tests."""
    _clear_registry()
    LifecycleManager.reset()
    Time._reset()
    Camera._reset_main()
    GameManager.instance = None
    yield
    _clear_registry()
    LifecycleManager.reset()
    Time._reset()
    Camera._reset_main()
    GameManager.instance = None


def _create_pipe_prefab() -> GameObject:
    """Create the pipe prefab template matching run_flappy_bird.py."""
    prefab = GameObject("Pipes")
    prefab.active = False

    pipes_comp = prefab.add_component(Pipes)

    top_go = GameObject("Top", tag="Obstacle")
    top_go.transform.set_parent(prefab.transform)
    sr_top = top_go.add_component(SpriteRenderer)
    sr_top.size = Vector2(1.0, 8.0)
    col_top = top_go.add_component(BoxCollider2D)
    col_top.size = Vector2(1.0, 8.0)
    col_top.is_trigger = True
    rb_top = top_go.add_component(Rigidbody2D)
    rb_top.body_type = RigidbodyType2D.KINEMATIC

    bottom_go = GameObject("Bottom", tag="Obstacle")
    bottom_go.transform.set_parent(prefab.transform)
    sr_bottom = bottom_go.add_component(SpriteRenderer)
    sr_bottom.size = Vector2(1.0, 8.0)
    col_bottom = bottom_go.add_component(BoxCollider2D)
    col_bottom.size = Vector2(1.0, 8.0)
    col_bottom.is_trigger = True
    rb_bottom = bottom_go.add_component(Rigidbody2D)
    rb_bottom.body_type = RigidbodyType2D.KINEMATIC

    scoring_go = GameObject("Scoring", tag="Scoring")
    scoring_go.transform.set_parent(prefab.transform)
    col_scoring = scoring_go.add_component(BoxCollider2D)
    col_scoring.size = Vector2(1.0, 6.0)
    col_scoring.is_trigger = True
    rb_scoring = scoring_go.add_component(Rigidbody2D)
    rb_scoring.body_type = RigidbodyType2D.KINEMATIC

    pipes_comp.top = top_go.transform
    pipes_comp.bottom = bottom_go.transform

    return prefab


def _setup_minimal_scene():
    """Set up a minimal Flappy Bird scene for integration testing."""
    pm = PhysicsManager.instance()
    pm.gravity = Vector2(0, 0)

    cam_go = GameObject("MainCamera")
    cam = cam_go.add_component(Camera)
    cam.orthographic_size = 5.0

    player_go = GameObject("Player")
    player_go.transform.position = Vector3(-2, 0, 0)
    sr_player = player_go.add_component(SpriteRenderer)
    sr_player.size = Vector2(0.8, 0.6)
    col_player = player_go.add_component(BoxCollider2D)
    col_player.size = Vector2(0.6, 0.4)
    col_player.is_trigger = True
    rb_player = player_go.add_component(Rigidbody2D)
    rb_player.body_type = RigidbodyType2D.KINEMATIC
    player_comp = player_go.add_component(Player)

    pipe_prefab = _create_pipe_prefab()

    spawner_go = GameObject("Spawner")
    spawner_go.transform.position = Vector3(8, 0, 0)
    spawner_comp = spawner_go.add_component(Spawner)
    spawner_comp.prefab = pipe_prefab
    spawner_comp.spawn_rate = 1.0
    spawner_comp.min_height = -1.0
    spawner_comp.max_height = 1.0
    spawner_comp.vertical_gap = 3.5

    bg_go = GameObject("Background")
    bg_parallax = bg_go.add_component(Parallax)
    bg_parallax.animation_speed = 0.5
    bg_parallax.wrap_width = 20.0

    # UI
    score_go = GameObject("ScoreText")
    score_text = score_go.add_component(Text)
    score_text.text = "0"

    game_over_go = GameObject("GameOver")
    game_over_go.active = False

    play_button_go = GameObject("PlayButton")

    gm_go = GameObject("GameManager")
    gm = gm_go.add_component(GameManager)
    gm.player = player_comp
    gm.spawner = spawner_comp
    gm.score_text = score_text
    gm.play_button = play_button_go
    gm.game_over_display = game_over_go

    return {
        "player": player_comp,
        "spawner": spawner_comp,
        "game_manager": gm,
        "score_text": score_text,
        "play_button": play_button_go,
        "game_over": game_over_go,
        "parallax": bg_parallax,
    }


def _run_frame(lm, dt=0.016):
    """Simulate one frame of the lifecycle."""
    Time._delta_time = dt
    Time._time += dt
    Time._frame_count += 1
    lm.process_awake_queue()
    lm.process_start_queue()
    lm.run_fixed_update()
    lm.run_update()
    lm.run_late_update()


class TestSceneSetup:
    """Verify all GameObjects are created and wired correctly."""

    def test_game_manager_singleton(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        assert GameManager.instance is scene["game_manager"]

    def test_player_exists(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        assert scene["player"] is not None
        assert scene["player"].game_object.name == "Player"

    def test_spawner_exists(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        assert scene["spawner"] is not None
        assert scene["spawner"].prefab is not None

    def test_camera_main_set(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        assert Camera.main is not None


class TestGameStartsPaused:
    """Verify game starts paused: Time.timeScale = 0, player disabled."""

    def test_time_scale_zero_after_start(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        # GameManager.start() calls self.pause() which sets timeScale to 0
        assert Time.time_scale == 0.0, f"Expected timeScale=0, got {Time.time_scale}"

    def test_player_disabled_after_start(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        assert scene["player"].enabled is False, "Player should be disabled when paused"


class TestPlayResumesGame:
    """Verify play() sets timeScale=1 and enables player."""

    def test_play_sets_time_scale(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        # Now play
        scene["game_manager"].play()
        assert Time.time_scale == 1.0

    def test_play_enables_player(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        scene["game_manager"].play()
        assert scene["player"].enabled is True

    def test_play_resets_score(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        scene["game_manager"].increase_score()
        scene["game_manager"].increase_score()
        scene["game_manager"].play()
        assert scene["game_manager"].score == 0

    def test_play_hides_buttons(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        scene["game_manager"].play()
        assert scene["play_button"].active is False
        assert scene["game_over"].active is False


class TestPipeSpawning:
    """Verify pipes spawn and move during gameplay."""

    def test_pipes_spawn_after_play(self):
        """After play() and enough time, InvokeRepeating should spawn pipes."""
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        scene["game_manager"].play()

        # Run frames for >1 spawn_rate to trigger spawning
        # spawn_rate = 1.0, so we need >1.0s of frames
        for _ in range(80):
            _run_frame(lm, 0.016)

        # Check for Pipes components
        pipes_found = GameObject.find_objects_of_type(Pipes)
        assert len(pipes_found) >= 1, f"Expected at least 1 pipe spawned, found {len(pipes_found)}"

    def test_pipes_move_left(self):
        """Pipes should move leftward each frame."""
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        scene["game_manager"].play()

        # Run enough frames to spawn a pipe
        for _ in range(80):
            _run_frame(lm, 0.016)

        pipes_found = GameObject.find_objects_of_type(Pipes)
        if len(pipes_found) == 0:
            pytest.skip("No pipes spawned — cannot test movement")

        pipe = pipes_found[0]
        x_before = pipe.transform.position.x

        # Run a few more frames
        for _ in range(10):
            _run_frame(lm, 0.016)

        x_after = pipe.transform.position.x
        assert x_after < x_before, f"Pipe should move left: {x_before} -> {x_after}"


class TestPipeDestruction:
    """Verify pipes are destroyed when off-screen."""

    def test_pipe_destroyed_past_left_edge(self):
        """A pipe positioned far left should be destroyed on update."""
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        scene["game_manager"].play()

        # Manually create a pipe far to the left
        pipe_go = GameObject("TestPipe")
        pipe_go.transform.position = Vector3(-20, 0, 0)
        pipe_comp = pipe_go.add_component(Pipes)
        pipe_comp.speed = 5.0

        # Process the new pipe through lifecycle
        lm.process_awake_queue()
        lm.process_start_queue()

        # Run a frame — pipe should be destroyed because it's past left_edge
        _run_frame(lm, 0.016)

        assert pipe_go.active is False, "Pipe past left edge should be destroyed"


class TestGameOver:
    """Verify game_over() pauses and shows UI."""

    def test_game_over_pauses(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        scene["game_manager"].play()

        scene["game_manager"].game_over()
        assert Time.time_scale == 0.0

    def test_game_over_disables_player(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        scene["game_manager"].play()

        scene["game_manager"].game_over()
        assert scene["player"].enabled is False

    def test_game_over_shows_ui(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        scene["game_manager"].play()

        scene["game_manager"].game_over()
        assert scene["play_button"].active is True
        assert scene["game_over"].active is True


class TestScoring:
    """Verify score tracking works."""

    def test_increase_score(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        scene["game_manager"].increase_score()
        assert scene["game_manager"].score == 1

    def test_score_text_updates(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        scene["game_manager"].increase_score()
        scene["game_manager"].increase_score()
        assert scene["score_text"].text == "2"


class TestParallax:
    """Verify parallax scrolling works."""

    def test_background_scrolls_left(self):
        scene = _setup_minimal_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        Time.set_time_scale(1.0)
        x_before = scene["parallax"].transform.position.x

        for _ in range(10):
            _run_frame(lm, 0.016)

        x_after = scene["parallax"].transform.position.x
        assert x_after < x_before, f"Parallax should scroll left: {x_before} -> {x_after}"
