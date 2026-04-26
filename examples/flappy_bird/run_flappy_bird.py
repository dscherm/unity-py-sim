"""Run Flappy Bird in the Python Unity simulator.

Controls:
  Space or Left Click: Flap
  ESC: Quit

Source: zigurous/unity-flappy-bird-tutorial (5 C# scripts)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.core import GameObject, MonoBehaviour
from src.engine.rendering.camera import Camera
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D
from src.engine.math.vector import Vector2, Vector3
from src.engine.input_manager import Input
from src.engine.ui import Canvas, RectTransform, Text, Image, Button, TextAnchor
from src.engine.app import run
from src.assets.resolver import set_active_game

from flappy_bird_python.player import Player
from flappy_bird_python.game_manager import GameManager
from flappy_bird_python.pipes import Pipes
from flappy_bird_python.spawner import Spawner
from flappy_bird_python.parallax import Parallax


class QuitHandler(MonoBehaviour):
    def update(self):
        if Input.get_key_down("escape"):
            from src.engine.rendering.display import DisplayManager
            DisplayManager.instance().request_quit()


class PlayButtonHandler(MonoBehaviour):
    """Handles play button click — calls GameManager.play()."""
    def update(self):
        if Input.get_mouse_button_down(0) or Input.get_key_down("space"):
            if GameManager.instance is not None:
                # Only respond when game is paused (play button visible)
                if GameManager.instance.play_button is not None and GameManager.instance.play_button.active:
                    GameManager.instance.play()


def create_pipe_prefab() -> GameObject:
    """Create the Pipes prefab template (parent + top/bottom children + scoring trigger)."""
    prefab = GameObject("Pipes")
    prefab.active = False  # Template — not rendered

    pipes_comp = prefab.add_component(Pipes)

    # Top pipe child
    top_go = GameObject("Top", tag="Obstacle")
    top_go.transform.set_parent(prefab.transform)
    top_go.transform.position = Vector3(0, 0, 0)
    sr_top = top_go.add_component(SpriteRenderer)
    sr_top.color = (80, 180, 50)
    sr_top.size = Vector2(1.0, 8.0)
    sr_top.asset_ref = "pipe"
    col_top = top_go.add_component(BoxCollider2D)
    col_top.size = Vector2(1.0, 8.0)
    col_top.is_trigger = True
    rb_top = top_go.add_component(Rigidbody2D)
    rb_top.body_type = RigidbodyType2D.KINEMATIC

    # Bottom pipe child
    bottom_go = GameObject("Bottom", tag="Obstacle")
    bottom_go.transform.set_parent(prefab.transform)
    bottom_go.transform.position = Vector3(0, 0, 0)
    sr_bottom = bottom_go.add_component(SpriteRenderer)
    sr_bottom.color = (80, 180, 50)
    sr_bottom.size = Vector2(1.0, 8.0)
    sr_bottom.asset_ref = "pipe"
    col_bottom = bottom_go.add_component(BoxCollider2D)
    col_bottom.size = Vector2(1.0, 8.0)
    col_bottom.is_trigger = True
    rb_bottom = bottom_go.add_component(Rigidbody2D)
    rb_bottom.body_type = RigidbodyType2D.KINEMATIC

    # Scoring trigger child (invisible, between pipes)
    scoring_go = GameObject("Scoring", tag="Scoring")
    scoring_go.transform.set_parent(prefab.transform)
    scoring_go.transform.position = Vector3(0, 0, 0)
    col_scoring = scoring_go.add_component(BoxCollider2D)
    col_scoring.size = Vector2(1.0, 6.0)
    col_scoring.is_trigger = True
    rb_scoring = scoring_go.add_component(Rigidbody2D)
    rb_scoring.body_type = RigidbodyType2D.KINEMATIC

    pipes_comp.top = top_go.transform
    pipes_comp.bottom = bottom_go.transform

    return prefab


def setup_scene():
    set_active_game("flappy_bird")

    pm = PhysicsManager.instance()
    pm.gravity = Vector2(0, 0)  # Player handles its own gravity

    # Camera
    cam_go = GameObject("MainCamera")
    cam = cam_go.add_component(Camera)
    cam.orthographic_size = 5.0
    cam.background_color = (113, 197, 207)  # Sky blue

    # Player (bird)
    player_go = GameObject("Player")
    player_go.transform.position = Vector3(-2, 0, 0)
    sr_player = player_go.add_component(SpriteRenderer)
    sr_player.color = (255, 200, 50)  # Yellow bird
    sr_player.size = Vector2(0.8, 0.6)
    sr_player.asset_ref = "bird_01"
    col_player = player_go.add_component(BoxCollider2D)
    col_player.size = Vector2(0.6, 0.4)
    col_player.is_trigger = True
    rb_player = player_go.add_component(Rigidbody2D)
    rb_player.body_type = RigidbodyType2D.KINEMATIC
    player_comp = player_go.add_component(Player)

    # Ground (bottom boundary with Obstacle tag)
    ground_go = GameObject("Ground", tag="Obstacle")
    ground_go.transform.position = Vector3(0, -5.5, 0)
    sr_ground = ground_go.add_component(SpriteRenderer)
    sr_ground.color = (200, 180, 100)
    sr_ground.size = Vector2(20.0, 1.0)
    sr_ground.asset_ref = "ground"
    col_ground = ground_go.add_component(BoxCollider2D)
    col_ground.size = Vector2(20.0, 1.0)
    col_ground.is_trigger = True
    rb_ground = ground_go.add_component(Rigidbody2D)
    rb_ground.body_type = RigidbodyType2D.STATIC

    # Ceiling (top boundary with Obstacle tag)
    ceiling_go = GameObject("Ceiling", tag="Obstacle")
    ceiling_go.transform.position = Vector3(0, 5.5, 0)
    col_ceiling = ceiling_go.add_component(BoxCollider2D)
    col_ceiling.size = Vector2(20.0, 1.0)
    col_ceiling.is_trigger = True
    rb_ceiling = ceiling_go.add_component(Rigidbody2D)
    rb_ceiling.body_type = RigidbodyType2D.STATIC

    # Pipe prefab
    pipe_prefab = create_pipe_prefab()

    # Spawner
    spawner_go = GameObject("Spawner")
    spawner_go.transform.position = Vector3(8, 0, 0)  # Spawn off right edge
    spawner_comp = spawner_go.add_component(Spawner)
    spawner_comp.prefab = pipe_prefab
    spawner_comp.spawn_rate = 1.5
    spawner_comp.min_height = -1.5
    spawner_comp.max_height = 1.5
    spawner_comp.vertical_gap = 3.5

    # Background parallax
    bg_go = GameObject("Background")
    bg_go.transform.position = Vector3(0, 0, 0)
    sr_bg = bg_go.add_component(SpriteRenderer)
    sr_bg.color = (113, 197, 207)
    sr_bg.size = Vector2(20.0, 12.0)
    sr_bg.sorting_order = -10
    sr_bg.asset_ref = "background"
    bg_parallax = bg_go.add_component(Parallax)
    bg_parallax.animation_speed = 0.5
    bg_parallax.wrap_width = 20.0

    # Ground parallax
    ground_parallax_go = GameObject("GroundParallax")
    ground_parallax_go.transform.position = Vector3(0, -5.0, 0)
    sr_gp = ground_parallax_go.add_component(SpriteRenderer)
    sr_gp.color = (200, 180, 100)
    sr_gp.size = Vector2(20.0, 0.5)
    sr_gp.sorting_order = 5
    sr_gp.asset_ref = "ground"
    gp_parallax = ground_parallax_go.add_component(Parallax)
    gp_parallax.animation_speed = 2.0
    gp_parallax.wrap_width = 20.0

    # UI Canvas
    canvas_go = GameObject("Canvas")
    canvas = canvas_go.add_component(Canvas)

    # Score text
    score_go = GameObject("ScoreText")
    score_go.transform.set_parent(canvas_go.transform)
    rt_score = score_go.add_component(RectTransform)
    rt_score.anchored_position = Vector2(400, 30)
    rt_score.size_delta = Vector2(200, 50)
    score_text = score_go.add_component(Text)
    score_text.text = "0"
    score_text.font_size = 48
    score_text.color = (255, 255, 255)
    score_text.alignment = TextAnchor.UPPER_CENTER

    # Game Over display
    game_over_go = GameObject("GameOver")
    game_over_go.active = False
    rt_go = game_over_go.add_component(RectTransform)
    rt_go.anchored_position = Vector2(400, 200)
    rt_go.size_delta = Vector2(300, 60)
    game_over_text = game_over_go.add_component(Text)
    game_over_text.text = "GAME OVER"
    game_over_text.font_size = 48
    game_over_text.color = (255, 50, 50)
    game_over_text.alignment = TextAnchor.MIDDLE_CENTER

    # Play button display
    play_button_go = GameObject("PlayButton")
    rt_pb = play_button_go.add_component(RectTransform)
    rt_pb.anchored_position = Vector2(400, 300)
    rt_pb.size_delta = Vector2(200, 50)
    play_button_text = play_button_go.add_component(Text)
    play_button_text.text = "CLICK TO PLAY"
    play_button_text.font_size = 32
    play_button_text.color = (255, 255, 255)
    play_button_text.alignment = TextAnchor.MIDDLE_CENTER

    # Game Manager
    gm_go = GameObject("GameManager")
    gm = gm_go.add_component(GameManager)
    gm.player = player_comp
    gm.spawner = spawner_comp
    gm.score_text = score_text
    gm.play_button = play_button_go
    gm.game_over_display = game_over_go

    # Play button handler
    pbh_go = GameObject("PlayButtonHandler")
    pbh_go.add_component(PlayButtonHandler)

    # Quit handler
    quit_go = GameObject("QuitHandler")
    quit_go.add_component(QuitHandler)


if __name__ == "__main__":
    headless = "--headless" in sys.argv
    max_frames = None
    if "--frames" in sys.argv:
        idx = sys.argv.index("--frames")
        max_frames = int(sys.argv[idx + 1])

    print("Flappy Bird -- Space/Click to flap, ESC to quit")
    run(setup_scene, width=800, height=600, headless=headless, max_frames=max_frames,
        title="Flappy Bird")
