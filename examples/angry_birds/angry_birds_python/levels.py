"""Level definitions for Angry Birds."""

from src.engine.core import GameObject
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D, PhysicsMaterial2D
from src.engine.rendering.camera import Camera
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.debug import Debug
from src.engine.scene import SceneManager

from src.engine.audio import AudioSource

from .bird import Bird
from .brick import Brick
from .pig import Pig
from .destroyer import Destroyer
from .slingshot import Slingshot
from .game_manager import GameManager


class _QuitHandler:
    """Mixin — not a standalone MonoBehaviour, used by levels."""
    pass


def _make_bird(name, pos):
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
    sr.asset_ref = "bird_red"
    audio = bird_go.add_component(AudioSource)  # throw sound
    audio.clip_ref = "bird_launch_sfx"
    bird_comp = bird_go.add_component(Bird)
    return bird_go


def _make_brick(name, pos, size, health, brick_mat):
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
    sr.asset_ref = "brick_wood"
    audio = brick_go.add_component(AudioSource)  # impact sound
    audio.clip_ref = "brick_break_sfx"
    brick_comp = brick_go.add_component(Brick)
    brick_comp.health = health
    brick_comp.max_health = health
    return brick_go


def _make_pig(name, pos):
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
    sr.asset_ref = "pig_normal"
    audio = pig_go.add_component(AudioSource)  # collision sound
    audio.clip_ref = "pig_hit_sfx"
    pig_comp = pig_go.add_component(Pig)
    return pig_go


def _make_destroyer(name, pos, size):
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
    return dest_go


def _setup_shared():
    """Create shared objects: camera, ground, slingshot, destroyers."""
    pm = PhysicsManager.instance()
    pm.gravity = Vector2(0, -9.81)

    cam_go = GameObject("MainCamera")
    cam = cam_go.add_component(Camera)
    cam.orthographic_size = 6.0
    cam.background_color = (135, 200, 235)

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
    sr_g.asset_ref = "ground_grass"

    slingshot_go = GameObject("Slingshot")
    slingshot_go.transform.position = Vector2(-5, -3.5)
    sling = slingshot_go.add_component(Slingshot)
    sr_s = slingshot_go.add_component(SpriteRenderer)
    sr_s.color = (120, 80, 40)
    sr_s.size = Vector2(0.3, 1.5)
    sr_s.asset_ref = "slingshot"

    _make_destroyer("Destroyer_Bottom", Vector2(0, -10), Vector2(40, 2))
    _make_destroyer("Destroyer_Left", Vector2(-18, 0), Vector2(2, 30))
    _make_destroyer("Destroyer_Right", Vector2(18, 0), Vector2(2, 30))

    return sling


def setup_level_1():
    """Level 1: Simple tower with 2 pigs, 3 birds."""
    sling = _setup_shared()
    brick_mat = PhysicsMaterial2D(bounciness=0.2, friction=0.6)

    bird1 = _make_bird("Bird_1", Vector2(-5, -3.5))
    bird2 = _make_bird("Bird_2", Vector2(-7, -4.2))
    bird3 = _make_bird("Bird_3", Vector2(-8, -4.2))
    sling.bird_to_throw = bird1

    _make_brick("B_pL", Vector2(4, -4.0), Vector2(0.4, 1.0), 70, brick_mat)
    _make_brick("B_pR", Vector2(6, -4.0), Vector2(0.4, 1.0), 70, brick_mat)
    _make_brick("B_b1", Vector2(5, -3.2), Vector2(2.5, 0.3), 50, brick_mat)
    _make_brick("B_uL", Vector2(4.5, -2.7), Vector2(0.4, 0.7), 40, brick_mat)
    _make_brick("B_uR", Vector2(5.5, -2.7), Vector2(0.4, 0.7), 40, brick_mat)
    _make_brick("B_cap", Vector2(5, -2.1), Vector2(1.5, 0.3), 90, brick_mat)

    _make_pig("Pig_1", Vector2(5, -3.7))
    _make_pig("Pig_2", Vector2(6.5, -4.2))

    gm_go = GameObject("GameManager")
    gm = gm_go.add_component(GameManager)
    GameManager.reset()


def setup_level_2():
    """Level 2: Fortress with 3 pigs behind walls, 3 birds."""
    sling = _setup_shared()
    brick_mat = PhysicsMaterial2D(bounciness=0.15, friction=0.7)

    bird1 = _make_bird("Bird_1", Vector2(-5, -3.5))
    bird2 = _make_bird("Bird_2", Vector2(-7, -4.2))
    bird3 = _make_bird("Bird_3", Vector2(-8, -4.2))
    sling.bird_to_throw = bird1

    # Fortress: thick walls with pigs inside
    _make_brick("B_wL", Vector2(3.5, -3.5), Vector2(0.5, 2.0), 120, brick_mat)
    _make_brick("B_wR", Vector2(7.0, -3.5), Vector2(0.5, 2.0), 120, brick_mat)
    _make_brick("B_roof", Vector2(5.25, -2.2), Vector2(4.0, 0.4), 100, brick_mat)
    _make_brick("B_floor", Vector2(5.25, -4.3), Vector2(4.0, 0.3), 80, brick_mat)
    _make_brick("B_mid", Vector2(5.25, -3.2), Vector2(0.3, 1.5), 50, brick_mat)

    _make_pig("Pig_1", Vector2(4.3, -3.7))
    _make_pig("Pig_2", Vector2(6.2, -3.7))
    _make_pig("Pig_3", Vector2(5.25, -2.8))

    gm_go = GameObject("GameManager")
    gm = gm_go.add_component(GameManager)
    GameManager.reset()


def register_all_levels():
    """Register both levels with SceneManager."""
    SceneManager.register_scene("level_1", setup_level_1)
    SceneManager.register_scene("level_2", setup_level_2)
