"""Run Angry Birds in the Python Unity simulator.

Controls:
  Click to start
  Click + drag bird to aim slingshot
  Release to launch
  ESC: Quit
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.core import GameObject, MonoBehaviour
from src.engine.lifecycle import LifecycleManager
from src.engine.rendering.camera import Camera
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D, PhysicsMaterial2D
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.debug import Debug
from src.engine.app import run

from angry_birds_python.bird import Bird
from angry_birds_python.brick import Brick
from angry_birds_python.pig import Pig
from angry_birds_python.destroyer import Destroyer
from angry_birds_python.slingshot import Slingshot
from angry_birds_python.game_manager import GameManager


class QuitHandler(MonoBehaviour):
    def update(self):
        if Input.get_key_down("escape"):
            from src.engine.rendering.display import DisplayManager
            DisplayManager.instance().request_quit()
        Debug.tick(0.016)


def _make_bird(name, pos, lm):
    """Create a bird GameObject at a waiting position."""
    bird_go = GameObject(name, tag="Bird")
    bird_go.transform.position = pos
    rb = bird_go.add_component(Rigidbody2D)
    rb.mass = 1.0
    col = bird_go.add_component(CircleCollider2D)
    col.radius = 0.3
    col.shared_material = PhysicsMaterial2D(bounciness=0.3, friction=0.5)
    col.build()
    sr = bird_go.add_component(SpriteRenderer)
    sr.color = (220, 50, 50)
    sr.size = Vector2(0.6, 0.6)
    bird_comp = bird_go.add_component(Bird)
    lm.register_component(bird_comp)
    return bird_go


def _make_brick(name, pos, size, health, brick_mat, lm):
    """Create a destructible brick."""
    brick_go = GameObject(name, tag="Brick")
    brick_go.transform.position = pos
    rb = brick_go.add_component(Rigidbody2D)
    rb.mass = 0.5
    rb._body.position = (pos.x, pos.y)
    col = brick_go.add_component(BoxCollider2D)
    col.size = size
    col.shared_material = brick_mat
    col.build()
    sr = brick_go.add_component(SpriteRenderer)
    sr.color = (180, 130, 70)
    sr.size = size
    brick_comp = brick_go.add_component(Brick)
    brick_comp.health = health
    brick_comp.max_health = health
    lm.register_component(brick_comp)
    return brick_go


def _make_pig(name, pos, lm):
    """Create a pig target."""
    pig_go = GameObject(name, tag="Pig")
    pig_go.transform.position = pos
    rb = pig_go.add_component(Rigidbody2D)
    rb.mass = 0.8
    rb._body.position = (pos.x, pos.y)
    col = pig_go.add_component(CircleCollider2D)
    col.radius = 0.3
    col.shared_material = PhysicsMaterial2D(bounciness=0.1, friction=0.5)
    col.build()
    sr = pig_go.add_component(SpriteRenderer)
    sr.color = (100, 200, 80)
    sr.size = Vector2(0.6, 0.6)
    pig_comp = pig_go.add_component(Pig)
    lm.register_component(pig_comp)
    return pig_go


def _make_destroyer(name, pos, size, lm):
    """Create a trigger zone that destroys stray objects."""
    dest_go = GameObject(name)
    dest_go.transform.position = pos
    rb = dest_go.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.STATIC
    rb._body.position = (pos.x, pos.y)
    col = dest_go.add_component(BoxCollider2D)
    col.size = size
    col.is_trigger = True
    col.build()
    dest_comp = dest_go.add_component(Destroyer)
    lm.register_component(dest_comp)
    return dest_go


def setup_scene():
    lm = LifecycleManager.instance()
    pm = PhysicsManager.instance()
    pm.gravity = Vector2(0, -9.81)

    # Camera
    cam_go = GameObject("MainCamera")
    cam = cam_go.add_component(Camera)
    cam.orthographic_size = 6.0
    cam.background_color = (135, 200, 235)
    lm.register_component(cam)

    # Ground
    ground_mat = PhysicsMaterial2D(bounciness=0.1, friction=0.8)
    ground = GameObject("Ground", tag="Ground")
    ground.transform.position = Vector2(0, -5)
    rb_g = ground.add_component(Rigidbody2D)
    rb_g.body_type = RigidbodyType2D.STATIC
    rb_g._body.position = (0, -5)
    col_g = ground.add_component(BoxCollider2D)
    col_g.size = Vector2(30, 1)
    col_g.shared_material = ground_mat
    col_g.build()
    sr_g = ground.add_component(SpriteRenderer)
    sr_g.color = (80, 160, 60)
    sr_g.size = Vector2(30, 1)

    # Slingshot
    slingshot_go = GameObject("Slingshot")
    slingshot_go.transform.position = Vector2(-5, -3.5)
    sling = slingshot_go.add_component(Slingshot)
    lm.register_component(sling)
    sr_s = slingshot_go.add_component(SpriteRenderer)
    sr_s.color = (120, 80, 40)
    sr_s.size = Vector2(0.3, 1.5)

    # Three birds at waiting positions
    bird1 = _make_bird("Bird_1", Vector2(-5, -3.5), lm)
    bird2 = _make_bird("Bird_2", Vector2(-7, -4.2), lm)
    bird3 = _make_bird("Bird_3", Vector2(-8, -4.2), lm)

    # Wire first bird to slingshot
    sling.bird_to_throw = bird1

    # Structure — brick tower with varied health
    brick_mat = PhysicsMaterial2D(bounciness=0.2, friction=0.6)
    # fmt: off
    bricks = [
        # Two pillars (tall, medium health)
        ("Brick_pillar_L", Vector2(4, -4.0), Vector2(0.4, 1.0), 70),
        ("Brick_pillar_R", Vector2(6, -4.0), Vector2(0.4, 1.0), 70),
        # Bottom beam
        ("Brick_beam_1",   Vector2(5, -3.2), Vector2(2.5, 0.3), 50),
        # Second level pillars (shorter, weaker)
        ("Brick_upper_L",  Vector2(4.5, -2.7), Vector2(0.4, 0.7), 40),
        ("Brick_upper_R",  Vector2(5.5, -2.7), Vector2(0.4, 0.7), 40),
        # Top cap (wide, strong)
        ("Brick_cap",      Vector2(5, -2.1), Vector2(1.5, 0.3), 90),
    ]
    # fmt: on
    for name, pos, size, health in bricks:
        _make_brick(name, pos, size, health, brick_mat, lm)

    # Two pigs — one inside structure, one behind
    _make_pig("Pig_1", Vector2(5, -3.7), lm)
    _make_pig("Pig_2", Vector2(6.5, -4.2), lm)

    # Boundary destroyers (trigger zones off-screen)
    _make_destroyer("Destroyer_Bottom", Vector2(0, -10), Vector2(40, 2), lm)
    _make_destroyer("Destroyer_Left", Vector2(-18, 0), Vector2(2, 30), lm)
    _make_destroyer("Destroyer_Right", Vector2(18, 0), Vector2(2, 30), lm)

    # Game manager
    gm_go = GameObject("GameManager")
    gm = gm_go.add_component(GameManager)
    GameManager.reset()
    lm.register_component(gm)

    # Quit handler
    quit_go = GameObject("QuitHandler")
    qh = quit_go.add_component(QuitHandler)
    lm.register_component(qh)


if __name__ == "__main__":
    headless = "--headless" in sys.argv
    max_frames = None
    if "--frames" in sys.argv:
        idx = sys.argv.index("--frames")
        max_frames = int(sys.argv[idx + 1])

    print("Angry Birds — Click to start, drag bird to aim, release to launch, ESC to quit")
    run(setup_scene, width=900, height=600, headless=headless, max_frames=max_frames,
        title="Angry Birds — Click to Start")
