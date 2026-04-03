"""Integration tests for Angry Birds example — runs real game loop headless."""

import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import CircleCollider2D, PhysicsMaterial2D
from src.engine.rendering.camera import Camera
from src.engine.rendering.display import DisplayManager
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.time_manager import Time
from src.engine.debug import Debug
from src.engine.app import run

from examples.angry_birds.angry_birds_python.bird import Bird
from examples.angry_birds.angry_birds_python.slingshot import Slingshot
from examples.angry_birds.angry_birds_python.enums import BirdState, SlingshotState


@pytest.fixture(autouse=True)
def _reset_all():
    """Reset all singletons before each test."""
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    DisplayManager.reset()
    Camera.main = None
    Input._reset()
    Time._reset()
    Debug._reset()
    yield
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    DisplayManager.reset()
    Camera.main = None
    Input._reset()
    Time._reset()
    Debug._reset()


def _minimal_scene():
    """Set up a minimal Angry Birds scene for integration testing."""
    from src.engine.rendering.renderer import SpriteRenderer
    from src.engine.physics.collider import BoxCollider2D

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
    ground = GameObject("Ground", tag="Ground")
    ground.transform.position = Vector2(0, -5)
    rb_g = ground.add_component(Rigidbody2D)
    rb_g.body_type = RigidbodyType2D.STATIC
    rb_g._body.position = (0, -5)
    col_g = ground.add_component(BoxCollider2D)
    col_g.size = Vector2(30, 1)
    col_g.build()

    # Slingshot
    slingshot_go = GameObject("Slingshot")
    slingshot_go.transform.position = Vector2(-5, -3.5)
    sling = slingshot_go.add_component(Slingshot)
    lm.register_component(sling)

    # Bird
    bird_go = GameObject("Bird", tag="Bird")
    bird_go.transform.position = Vector2(-5, -3.5)
    rb_b = bird_go.add_component(Rigidbody2D)
    rb_b.mass = 1.0
    col_b = bird_go.add_component(CircleCollider2D)
    col_b.radius = 0.3
    col_b.shared_material = PhysicsMaterial2D(bounciness=0.3, friction=0.5)
    col_b.build()
    bird_comp = bird_go.add_component(Bird)
    lm.register_component(bird_comp)

    sling.bird_to_throw = bird_go

    # Brick
    brick = GameObject("Brick_0", tag="Brick")
    brick.transform.position = Vector2(4, -4.0)
    rb_brick = brick.add_component(Rigidbody2D)
    rb_brick.mass = 0.5
    rb_brick._body.position = (4, -4.0)
    col_brick = brick.add_component(BoxCollider2D)
    col_brick.size = Vector2(0.4, 1.0)
    col_brick.build()

    # Pig
    pig = GameObject("Pig", tag="Pig")
    pig.transform.position = Vector2(5, -3.7)
    rb_pig = pig.add_component(Rigidbody2D)
    rb_pig.mass = 0.8
    rb_pig._body.position = (5, -3.7)
    col_pig = pig.add_component(CircleCollider2D)
    col_pig.radius = 0.3
    col_pig.build()


class TestAngryBirdsSceneRuns:
    """Verify the scene boots and runs headless without crashing."""

    def test_scene_runs_200_frames_no_errors(self):
        """The full scene should survive 200 headless frames without exceptions."""
        run(_minimal_scene, headless=True, max_frames=200)

    def test_scene_runs_with_full_setup(self):
        """Run using the actual run_angry_birds setup_scene (imported)."""
        # Import the real setup but we need to adjust import path
        import importlib
        import sys
        import os

        # Add the examples dir so the relative import inside run_angry_birds works
        examples_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "examples", "angry_birds"
        )
        sys.path.insert(0, os.path.abspath(examples_dir))
        try:
            from examples.angry_birds.run_angry_birds import setup_scene
            run(setup_scene, headless=True, max_frames=100)
        finally:
            sys.path.pop(0)


class TestBirdStartsKinematic:
    """Bird must begin kinematic so it doesn't fall before throw."""

    def test_bird_does_not_fall_before_throw(self):
        """A kinematic bird should stay at its starting Y position over many frames."""
        run(_minimal_scene, headless=True, max_frames=60)

        bird_go = GameObject.find("Bird")
        assert bird_go is not None, "Bird should exist after scene runs"
        # Bird should still be near its starting position (-3.5) since it's kinematic
        y = bird_go.transform.position.y
        assert abs(y - (-3.5)) < 0.5, (
            f"Bird Y={y} drifted from starting -3.5; kinematic body should not fall"
        )


class TestBirdThrowMakesBirdMove:
    """Manually triggering on_throw + setting velocity should make the bird move."""

    def test_bird_moves_after_throw(self):
        """After on_throw() and velocity set, bird position should change.

        BUG FOUND: pymunk zeroes mass/moment when switching KINEMATIC->DYNAMIC.
        Rigidbody2D.body_type setter does not restore them, so space.step()
        raises AssertionError for mass=0. We work around this by manually
        restoring mass/moment after on_throw(), which is what the engine
        should do automatically.
        """
        import pymunk

        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, -9.81)
        lm = LifecycleManager.instance()

        bird_go = GameObject("Bird", tag="Bird")
        bird_go.transform.position = Vector2(0, 0)
        rb = bird_go.add_component(Rigidbody2D)
        rb.mass = 1.0
        col = bird_go.add_component(CircleCollider2D)
        col.radius = 0.3
        col.shared_material = PhysicsMaterial2D(bounciness=0.3, friction=0.5)
        col.build()
        bird_comp = bird_go.add_component(Bird)
        lm.register_component(bird_comp)
        lm.process_awake_queue()
        lm.process_start_queue()

        start_pos = Vector2(bird_go.transform.position.x, bird_go.transform.position.y)

        # Throw the bird
        bird_comp.on_throw()

        # WORKAROUND for engine bug: pymunk zeroes mass/moment on
        # KINEMATIC -> DYNAMIC transition. Restore them manually.
        rb._body.mass = 1.0
        rb._body.moment = pymunk.moment_for_circle(1.0, 0, 0.3)

        rb.velocity = Vector2(10, 5)

        # Step physics several times
        for _ in range(30):
            pm.step(1.0 / 60.0)

        end_pos = bird_go.transform.position
        dist = Vector2.distance(start_pos, Vector2(end_pos.x, end_pos.y))
        assert dist > 0.5, (
            f"Bird should have moved after throw, but only moved {dist}"
        )

    def test_bug_kinematic_to_dynamic_loses_mass(self):
        """DISCOVERED BUG: Rigidbody2D.body_type setter does not preserve
        mass/moment when switching from KINEMATIC back to DYNAMIC.

        pymunk zeroes both values on that transition, and the engine does
        not restore them. This means space.step() will raise an assertion
        error if a bird is actually thrown during gameplay.
        """
        import pymunk

        bird_go = GameObject("BugBird")
        rb = bird_go.add_component(Rigidbody2D)
        rb.mass = 1.0
        original_mass = rb._body.mass
        original_moment = rb._body.moment

        # Switch to kinematic (as Bird.start does)
        rb.body_type = RigidbodyType2D.KINEMATIC
        # Switch back to dynamic (as Bird.on_throw does)
        rb.body_type = RigidbodyType2D.DYNAMIC

        # FIX: mass and moment are now restored after KINEMATIC->DYNAMIC switch
        assert rb._body.mass > 0, (
            "Mass should be restored after KINEMATIC->DYNAMIC switch"
        )
        assert rb._body.moment > 0, (
            "Moment should be restored after KINEMATIC->DYNAMIC switch"
        )


class TestSceneContainsBricksAndPig:
    """Scene must contain brick and pig game objects."""

    def test_bricks_exist(self):
        run(_minimal_scene, headless=True, max_frames=5)
        bricks = GameObject.find_game_objects_with_tag("Brick")
        assert len(bricks) >= 1, "At least one brick should exist"

    def test_pig_exists(self):
        run(_minimal_scene, headless=True, max_frames=5)
        pig = GameObject.find("Pig")
        assert pig is not None, "Pig should exist in scene"
        assert pig.tag == "Pig"
