"""Integration tests for Angry Birds gameplay systems: Brick, Pig, Destroyer, GameManager.

Tests run real engine components headless and verify observable outcomes match
Unity's documented behavior for OnCollisionEnter2D, OnTriggerEnter2D, and
game state transitions.
"""

import sys
import os
import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager, Collision2D
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import (
    BoxCollider2D,
    CircleCollider2D,
    PhysicsMaterial2D,
)
from src.engine.rendering.camera import Camera
from src.engine.rendering.display import DisplayManager
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.time_manager import Time
from src.engine.debug import Debug

from examples.angry_birds.angry_birds_python.brick import Brick
from examples.angry_birds.angry_birds_python.pig import Pig
from examples.angry_birds.angry_birds_python.destroyer import Destroyer
from examples.angry_birds.angry_birds_python.game_manager import GameManager
from examples.angry_birds.angry_birds_python.slingshot import Slingshot
from examples.angry_birds.angry_birds_python.bird import Bird
from examples.angry_birds.angry_birds_python.enums import GameState, SlingshotState
from examples.angry_birds.angry_birds_python.constants import Constants


@pytest.fixture(autouse=True)
def _reset_all():
    """Reset all singletons before and after each test."""
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    DisplayManager.reset()
    Camera.main = None
    Input._reset()
    Time._reset()
    Debug._reset()
    GameManager.reset()
    GameManager.current_level_index = 0
    yield
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    DisplayManager.reset()
    Camera.main = None
    Input._reset()
    Time._reset()
    Debug._reset()
    GameManager.reset()
    GameManager.current_level_index = 0


def _make_brick_go(pos=Vector2(0, 0), health=70.0):
    """Create a standalone brick with rigidbody and collider."""
    lm = LifecycleManager.instance()
    go = GameObject("TestBrick", tag="Brick")
    go.transform.position = pos
    rb = go.add_component(Rigidbody2D)
    rb.mass = 0.5
    rb._body.position = (pos.x, pos.y)
    col = go.add_component(BoxCollider2D)
    col.size = Vector2(1.0, 1.0)
    col.build()
    sr = go.add_component(SpriteRenderer)
    sr.color = (180, 130, 70)
    sr.size = Vector2(1.0, 1.0)
    brick = go.add_component(Brick)
    brick.health = health
    brick.max_health = health
    lm.register_component(brick)
    return go, brick


def _make_pig_go(pos=Vector2(0, 0), health=150.0):
    """Create a standalone pig with rigidbody and collider."""
    lm = LifecycleManager.instance()
    go = GameObject("TestPig", tag="Pig")
    go.transform.position = pos
    rb = go.add_component(Rigidbody2D)
    rb.mass = 0.8
    rb._body.position = (pos.x, pos.y)
    col = go.add_component(CircleCollider2D)
    col.radius = 0.3
    col.build()
    pig = go.add_component(Pig)
    pig.health = health
    lm.register_component(pig)
    return go, pig


def _make_bird_go(pos=Vector2(0, 0)):
    """Create a bird with rigidbody and collider."""
    lm = LifecycleManager.instance()
    go = GameObject("TestBird", tag="Bird")
    go.transform.position = pos
    rb = go.add_component(Rigidbody2D)
    rb.mass = 1.0
    col = go.add_component(CircleCollider2D)
    col.radius = 0.3
    col.shared_material = PhysicsMaterial2D(bounciness=0.3, friction=0.5)
    col.build()
    bird = go.add_component(Bird)
    lm.register_component(bird)
    return go, bird


# ---------------------------------------------------------------------------
# Full scene headless run
# ---------------------------------------------------------------------------
class TestFullSceneHeadless:
    """Run the full Angry Birds scene headless and verify no crashes."""

    def test_full_scene_300_frames_no_crash(self):
        """The full scene (from run_angry_birds.setup_scene) should survive
        300 headless frames without any exceptions."""
        from src.engine.app import run

        examples_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "examples", "angry_birds"
        )
        sys.path.insert(0, os.path.abspath(examples_dir))
        try:
            from examples.angry_birds.run_angry_birds import setup_scene
            # If this raises, the test fails with a traceback
            run(setup_scene, headless=True, max_frames=300)
        finally:
            sys.path.pop(0)


# ---------------------------------------------------------------------------
# Brick collision -> damage -> destruction
# ---------------------------------------------------------------------------
class TestBrickCollisionDestruction:
    """A brick receiving a high-velocity collision should be destroyed."""

    def test_brick_destroyed_by_high_velocity_collision(self):
        """Simulate OnCollisionEnter2D with velocity high enough to kill the brick.

        Unity contract: collision.relativeVelocity is the approach velocity
        between the two colliding bodies. Brick damage = magnitude * 10.
        A brick with 70 HP hit at magnitude 8 takes 80 damage -> destroyed.
        """
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        brick_go, brick = _make_brick_go(health=70.0)
        lm.process_awake_queue()
        lm.process_start_queue()

        # Create a collider object (the thing hitting the brick)
        projectile = GameObject("Projectile", tag="Bird")
        rb_proj = projectile.add_component(Rigidbody2D)
        rb_proj.mass = 1.0

        # Simulate collision with high relative velocity (magnitude 8 -> damage 80)
        collision = Collision2D(
            game_object=projectile,
            relative_velocity=Vector2(8, 0),  # magnitude = 8
        )
        brick.on_collision_enter_2d(collision)

        assert not brick_go.active, (
            "Brick with 70 HP hit at velocity magnitude 8 (damage=80) should be destroyed"
        )

    def test_brick_survives_low_velocity_collision(self):
        """A gentle bump (magnitude < 0.5, damage < 5) should be ignored."""
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        brick_go, brick = _make_brick_go(health=70.0)
        lm.process_awake_queue()
        lm.process_start_queue()

        projectile = GameObject("Nudge")
        rb_proj = projectile.add_component(Rigidbody2D)

        collision = Collision2D(
            game_object=projectile,
            relative_velocity=Vector2(0.3, 0),  # magnitude 0.3 -> damage 3 < 5
        )
        brick.on_collision_enter_2d(collision)

        assert brick_go.active, "Brick should survive a tiny bump"
        assert brick.health == 70.0, "Brick health should be unchanged after tiny bump"


# ---------------------------------------------------------------------------
# Pig + Bird collision -> instant kill
# ---------------------------------------------------------------------------
class TestPigBirdInstantKill:
    """A pig hit by a Bird-tagged object should be destroyed instantly,
    regardless of velocity."""

    def test_pig_destroyed_on_bird_collision(self):
        """Unity contract: OnCollisionEnter2D fires, pig checks tag == 'Bird',
        instantly destroys itself without checking damage."""
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        pig_go, pig = _make_pig_go(health=150.0)
        lm.process_awake_queue()
        lm.process_start_queue()

        bird = GameObject("Bird", tag="Bird")
        rb_bird = bird.add_component(Rigidbody2D)

        # Even zero velocity should kill the pig if tag is Bird
        collision = Collision2D(
            game_object=bird,
            relative_velocity=Vector2(0, 0),
        )
        pig.on_collision_enter_2d(collision)

        assert not pig_go.active, (
            "Pig should be instantly destroyed when hit by a Bird-tagged object, "
            "even at zero velocity"
        )

    def test_pig_survives_non_bird_low_velocity(self):
        """Pig should survive a collision from a non-bird object at low velocity."""
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        pig_go, pig = _make_pig_go(health=150.0)
        lm.process_awake_queue()
        lm.process_start_queue()

        debris = GameObject("Debris", tag="Brick")
        rb_debris = debris.add_component(Rigidbody2D)

        collision = Collision2D(
            game_object=debris,
            relative_velocity=Vector2(1, 0),  # damage = 10
        )
        pig.on_collision_enter_2d(collision)

        assert pig_go.active, "Pig should survive 10 damage when at 150 HP"
        assert pig.health == pytest.approx(140.0), "Pig should have taken 10 damage"


# ---------------------------------------------------------------------------
# GameManager win condition
# ---------------------------------------------------------------------------
class TestGameManagerWinCondition:
    """GameManager should detect all pigs destroyed and transition to WON."""

    def test_all_pigs_destroyed_triggers_won(self):
        """When all pigs are inactive, _all_pigs_destroyed returns True
        and the game should reach GameState.WON after the coroutine settles."""
        lm = LifecycleManager.instance()
        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, -9.81)

        # Camera (required for scene)
        cam_go = GameObject("MainCamera")
        cam = cam_go.add_component(Camera)
        cam.orthographic_size = 6.0
        lm.register_component(cam)

        # Slingshot
        sling_go = GameObject("Slingshot")
        sling_go.transform.position = Vector2(-5, -3.5)
        sling = sling_go.add_component(Slingshot)
        lm.register_component(sling)

        # One bird
        bird_go, bird_comp = _make_bird_go(Vector2(-5, -3.5))
        sling.bird_to_throw = bird_go

        # One pig -- destroy it immediately
        pig_go, pig_comp = _make_pig_go(Vector2(5, -3.7))

        # GameManager
        gm_go = GameObject("GameManager")
        gm = gm_go.add_component(GameManager)
        GameManager.reset()
        lm.register_component(gm)

        lm.process_awake_queue()
        lm.process_start_queue()

        # Verify GM found the pig
        assert len(gm.pigs) == 1

        # Destroy the pig
        GameObject.destroy(pig_go)

        # Now _all_pigs_destroyed should be True
        assert gm._all_pigs_destroyed(), (
            "After destroying all pigs, _all_pigs_destroyed should return True"
        )

        # Set level index past all levels so _next_turn goes to WON
        from examples.angry_birds.angry_birds_python.game_manager import LEVEL_NAMES
        GameManager.current_level_index = len(LEVEL_NAMES)

        # Simulate the _next_turn coroutine flow by calling it directly
        gen = gm._next_turn()
        # First yield is WaitForSeconds(1.0)
        wait = next(gen)
        from src.engine.coroutine import WaitForSeconds
        assert isinstance(wait, WaitForSeconds)

        # The coroutine should set state to WON and return
        try:
            next(gen)
            assert False, "Coroutine should have stopped after setting WON"
        except StopIteration:
            pass

        assert gm.game_state == GameState.WON, (
            "GameManager should transition to WON when all pigs destroyed and no more levels"
        )
