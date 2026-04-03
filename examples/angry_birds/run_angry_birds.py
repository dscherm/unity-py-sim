"""Run Angry Birds in the Python Unity simulator.

Controls:
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
from angry_birds_python.slingshot import Slingshot


class QuitHandler(MonoBehaviour):
    def update(self):
        if Input.get_key_down("escape"):
            from src.engine.rendering.display import DisplayManager
            DisplayManager.instance().request_quit()
        Debug.tick(0.016)


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

    # Bird
    bird_go = GameObject("Bird", tag="Bird")
    bird_go.transform.position = Vector2(-5, -3.5)
    rb_b = bird_go.add_component(Rigidbody2D)
    rb_b.mass = 1.0
    col_b = bird_go.add_component(CircleCollider2D)
    col_b.radius = 0.3
    col_b.shared_material = PhysicsMaterial2D(bounciness=0.3, friction=0.5)
    col_b.build()
    sr_b = bird_go.add_component(SpriteRenderer)
    sr_b.color = (220, 50, 50)
    sr_b.size = Vector2(0.6, 0.6)
    bird_comp = bird_go.add_component(Bird)
    lm.register_component(bird_comp)

    # Wire bird to slingshot
    sling.bird_to_throw = bird_go

    # Simple structure — brick tower
    brick_mat = PhysicsMaterial2D(bounciness=0.2, friction=0.6)
    brick_positions = [
        # Two pillars
        (Vector2(4, -4.0), Vector2(0.4, 1.0)),
        (Vector2(6, -4.0), Vector2(0.4, 1.0)),
        # Top beam
        (Vector2(5, -3.2), Vector2(2.5, 0.3)),
        # Second level pillars
        (Vector2(4.5, -2.7), Vector2(0.4, 0.7)),
        (Vector2(5.5, -2.7), Vector2(0.4, 0.7)),
        # Top piece
        (Vector2(5, -2.1), Vector2(1.5, 0.3)),
    ]

    for i, (pos, size) in enumerate(brick_positions):
        brick = GameObject(f"Brick_{i}", tag="Brick")
        brick.transform.position = pos
        rb_brick = brick.add_component(Rigidbody2D)
        rb_brick.mass = 0.5
        rb_brick._body.position = (pos.x, pos.y)
        col_brick = brick.add_component(BoxCollider2D)
        col_brick.size = size
        col_brick.shared_material = brick_mat
        col_brick.build()
        sr_brick = brick.add_component(SpriteRenderer)
        sr_brick.color = (180, 130, 70)
        sr_brick.size = size

    # Pig inside structure
    pig = GameObject("Pig", tag="Pig")
    pig.transform.position = Vector2(5, -3.7)
    rb_pig = pig.add_component(Rigidbody2D)
    rb_pig.mass = 0.8
    rb_pig._body.position = (5, -3.7)
    col_pig = pig.add_component(CircleCollider2D)
    col_pig.radius = 0.3
    col_pig.shared_material = PhysicsMaterial2D(bounciness=0.1, friction=0.5)
    col_pig.build()
    sr_pig = pig.add_component(SpriteRenderer)
    sr_pig.color = (100, 200, 80)
    sr_pig.size = Vector2(0.6, 0.6)

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

    print("Angry Birds — Click+drag bird to aim, release to launch, ESC to quit")
    run(setup_scene, width=900, height=600, headless=headless, max_frames=max_frames,
        title="Angry Birds — Click+Drag to Aim")
