"""Contract tests verifying Unity behavioral contracts for Angry Birds gameplay systems.

Expectations derived from Unity documentation, not from what the code does:
- OnCollisionEnter2D: collision.relativeVelocity is the approach velocity between bodies
- Brick damage formula: magnitude * 10
- Pig instant-kill on Bird tag is unconditional (no health/velocity check)
- Destroyer only destroys objects with specific tags
- GameManager._all_stopped: returns True when all tracked objects have velocity < MIN_VELOCITY
"""

import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager, Collision2D
from src.engine.physics.rigidbody import Rigidbody2D
from src.engine.physics.collider import (
    CircleCollider2D,
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
from examples.angry_birds.angry_birds_python.constants import Constants


@pytest.fixture(autouse=True)
def _reset_all():
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


# ---------------------------------------------------------------------------
# Unity OnCollisionEnter2D: collision.relativeVelocity contract
# ---------------------------------------------------------------------------
class TestCollisionRelativeVelocityContract:
    """Unity's Collision2D.relativeVelocity represents the approach velocity
    between the two colliding bodies. The engine's Collision2D dataclass
    must carry this as a Vector2 with a valid magnitude property."""

    def test_relative_velocity_has_magnitude(self):
        """Collision2D.relative_velocity.magnitude should equal the Euclidean
        length of the velocity vector."""
        col = Collision2D(
            game_object=GameObject("Dummy"),
            relative_velocity=Vector2(3, 4),
        )
        assert col.relative_velocity.magnitude == pytest.approx(5.0), (
            "Vector2(3,4) magnitude should be 5.0"
        )

    def test_zero_velocity_has_zero_magnitude(self):
        col = Collision2D(
            game_object=GameObject("Dummy"),
            relative_velocity=Vector2(0, 0),
        )
        assert col.relative_velocity.magnitude == pytest.approx(0.0)

    def test_collision_carries_game_object_reference(self):
        """Unity contract: collision.gameObject refers to the OTHER object."""
        other = GameObject("Other")
        col = Collision2D(game_object=other)
        assert col.game_object is other


# ---------------------------------------------------------------------------
# Brick damage formula: damage = relative_velocity.magnitude * 10
# ---------------------------------------------------------------------------
class TestBrickDamageFormulaContract:
    """The brick damage formula must be magnitude * 10, with a threshold
    of 5 damage minimum (tiny bumps ignored)."""

    def _make_brick(self, health=70.0):
        go = GameObject("Brick", tag="Brick")
        rb = go.add_component(Rigidbody2D)
        rb.mass = 0.5
        sr = go.add_component(SpriteRenderer)
        sr.color = (180, 130, 70)
        sr.size = Vector2(1, 1)
        brick = go.add_component(Brick)
        brick.health = health
        brick.max_health = health
        return go, brick

    def test_damage_equals_magnitude_times_10(self):
        """Brick at 100 HP hit at magnitude 5 should take exactly 50 damage."""
        go, brick = self._make_brick(health=100.0)
        other = GameObject("Hitter")
        other.add_component(Rigidbody2D)

        collision = Collision2D(
            game_object=other,
            relative_velocity=Vector2(5, 0),
        )
        brick.on_collision_enter_2d(collision)

        assert brick.health == pytest.approx(50.0), (
            "100 HP - (5 * 10) = 50 HP expected"
        )

    def test_damage_threshold_rejects_small_bumps(self):
        """Damage below 5 (velocity magnitude < 0.5) should be ignored entirely."""
        go, brick = self._make_brick(health=100.0)
        other = GameObject("Gentle")
        other.add_component(Rigidbody2D)

        collision = Collision2D(
            game_object=other,
            relative_velocity=Vector2(0.4, 0),  # damage = 4 < 5
        )
        brick.on_collision_enter_2d(collision)

        assert brick.health == pytest.approx(100.0), (
            "Damage 4 is below threshold 5; health should be unchanged"
        )

    def test_exact_threshold_boundary(self):
        """Damage of exactly 5 (magnitude 0.5) should be applied."""
        go, brick = self._make_brick(health=100.0)
        other = GameObject("Boundary")
        other.add_component(Rigidbody2D)

        collision = Collision2D(
            game_object=other,
            relative_velocity=Vector2(0.5, 0),  # damage = 5, not < 5
        )
        brick.on_collision_enter_2d(collision)

        assert brick.health == pytest.approx(95.0), (
            "Damage of exactly 5 should be applied: 100 - 5 = 95"
        )

    def test_no_rigidbody_on_other_means_no_damage(self):
        """If the other object has no Rigidbody2D, brick ignores the collision."""
        go, brick = self._make_brick(health=70.0)
        other = GameObject("NoRB")
        # No Rigidbody2D added

        collision = Collision2D(
            game_object=other,
            relative_velocity=Vector2(100, 0),
        )
        brick.on_collision_enter_2d(collision)

        assert brick.health == pytest.approx(70.0), (
            "Brick should not take damage from objects without Rigidbody2D"
        )


# ---------------------------------------------------------------------------
# Pig instant-kill on Bird tag: unconditional, no health check
# ---------------------------------------------------------------------------
class TestPigInstantKillContract:
    """When a Bird-tagged object collides with a pig, the pig is destroyed
    immediately. This is unconditional -- no velocity or health check."""

    def _make_pig(self, health=150.0):
        go = GameObject("Pig", tag="Pig")
        rb = go.add_component(Rigidbody2D)
        rb.mass = 0.8
        pig = go.add_component(Pig)
        pig.health = health
        return go, pig

    def test_bird_tag_kills_pig_at_zero_velocity(self):
        """Even at zero relative velocity, Bird tag means instant death."""
        go, pig = self._make_pig(health=150.0)
        bird = GameObject("Bird", tag="Bird")
        bird.add_component(Rigidbody2D)

        collision = Collision2D(
            game_object=bird,
            relative_velocity=Vector2(0, 0),
        )
        pig.on_collision_enter_2d(collision)

        assert not go.active, "Pig should die instantly from Bird, even at 0 velocity"

    def test_bird_tag_kills_pig_at_full_health(self):
        """Full health should not save a pig from a bird collision."""
        go, pig = self._make_pig(health=9999.0)
        bird = GameObject("Bird", tag="Bird")
        bird.add_component(Rigidbody2D)

        collision = Collision2D(
            game_object=bird,
            relative_velocity=Vector2(1, 0),
        )
        pig.on_collision_enter_2d(collision)

        assert not go.active, "Pig should die from Bird regardless of health"

    def test_non_bird_tag_does_not_instant_kill(self):
        """A Brick-tagged object should NOT instant-kill the pig."""
        go, pig = self._make_pig(health=150.0)
        brick = GameObject("Brick", tag="Brick")
        brick.add_component(Rigidbody2D)

        collision = Collision2D(
            game_object=brick,
            relative_velocity=Vector2(1, 0),  # damage = 10
        )
        pig.on_collision_enter_2d(collision)

        assert go.active, "Non-bird should not instant-kill pig"
        assert pig.health == pytest.approx(140.0)

    def test_pig_no_rigidbody_other_ignored(self):
        """If the colliding object has no Rigidbody2D, pig ignores entirely."""
        go, pig = self._make_pig(health=150.0)
        ghost = GameObject("Ghost", tag="Bird")
        # No Rigidbody2D

        collision = Collision2D(
            game_object=ghost,
            relative_velocity=Vector2(100, 0),
        )
        pig.on_collision_enter_2d(collision)

        assert go.active, "Pig should ignore collision from object without Rigidbody2D"


# ---------------------------------------------------------------------------
# Destroyer tag filter: only Bird/Pig/Brick
# ---------------------------------------------------------------------------
class TestDestroyerTagFilterContract:
    """Destroyer trigger zone should only destroy objects tagged Bird, Pig, or Brick.
    All other tags should pass through unharmed."""

    def _make_destroyer(self):
        go = GameObject("Destroyer")
        destroyer = go.add_component(Destroyer)
        return go, destroyer

    def test_destroys_bird_tag(self):
        _, destroyer = self._make_destroyer()
        bird = GameObject("Bird", tag="Bird")
        destroyer.on_trigger_enter_2d(bird)
        assert not bird.active, "Destroyer should destroy Bird-tagged objects"

    def test_destroys_pig_tag(self):
        _, destroyer = self._make_destroyer()
        pig = GameObject("Pig", tag="Pig")
        destroyer.on_trigger_enter_2d(pig)
        assert not pig.active, "Destroyer should destroy Pig-tagged objects"

    def test_destroys_brick_tag(self):
        _, destroyer = self._make_destroyer()
        brick = GameObject("Brick", tag="Brick")
        destroyer.on_trigger_enter_2d(brick)
        assert not brick.active, "Destroyer should destroy Brick-tagged objects"

    def test_ignores_ground_tag(self):
        _, destroyer = self._make_destroyer()
        ground = GameObject("Ground", tag="Ground")
        destroyer.on_trigger_enter_2d(ground)
        assert ground.active, "Destroyer should NOT destroy Ground-tagged objects"

    def test_ignores_untagged(self):
        _, destroyer = self._make_destroyer()
        obj = GameObject("Random", tag="Untagged")
        destroyer.on_trigger_enter_2d(obj)
        assert obj.active, "Destroyer should NOT destroy Untagged objects"

    def test_ignores_custom_tag(self):
        _, destroyer = self._make_destroyer()
        obj = GameObject("Custom", tag="PowerUp")
        destroyer.on_trigger_enter_2d(obj)
        assert obj.active, "Destroyer should NOT destroy custom-tagged objects"


# ---------------------------------------------------------------------------
# GameManager._all_stopped: velocity < MIN_VELOCITY
# ---------------------------------------------------------------------------
class TestGameManagerAllStoppedContract:
    """GameManager._all_stopped should return True only when all tracked
    objects (birds, pigs, bricks) have velocity below MIN_VELOCITY."""

    def _make_gm_with_objects(self):
        """Set up a GameManager with one bird and one pig, both at rest."""
        lm = LifecycleManager.instance()
        pm = PhysicsManager.instance()

        # Camera
        cam_go = GameObject("MainCamera")
        cam = cam_go.add_component(Camera)
        cam.orthographic_size = 6.0
        lm.register_component(cam)

        # Slingshot
        sling_go = GameObject("Slingshot")
        sling_go.transform.position = Vector2(-5, -3.5)
        sling = sling_go.add_component(Slingshot)
        lm.register_component(sling)

        # Bird
        bird_go = GameObject("Bird", tag="Bird")
        bird_go.transform.position = Vector2(-5, -3.5)
        rb_bird = bird_go.add_component(Rigidbody2D)
        rb_bird.mass = 1.0
        col_b = bird_go.add_component(CircleCollider2D)
        col_b.radius = 0.3
        col_b.build()
        bird_comp = bird_go.add_component(Bird)
        lm.register_component(bird_comp)
        sling.bird_to_throw = bird_go

        # Pig
        pig_go = GameObject("Pig", tag="Pig")
        pig_go.transform.position = Vector2(5, -3.7)
        rb_pig = pig_go.add_component(Rigidbody2D)
        rb_pig.mass = 0.8
        rb_pig._body.position = (5, -3.7)
        col_p = pig_go.add_component(CircleCollider2D)
        col_p.radius = 0.3
        col_p.build()

        # GameManager
        gm_go = GameObject("GameManager")
        gm = gm_go.add_component(GameManager)
        GameManager.reset()
        lm.register_component(gm)

        lm.process_awake_queue()
        lm.process_start_queue()

        return gm, rb_bird, rb_pig

    def test_all_stopped_when_all_at_rest(self):
        """When all tracked objects have zero velocity, _all_stopped returns True."""
        gm, rb_bird, rb_pig = self._make_gm_with_objects()
        # Both bodies at rest (velocity = 0)
        rb_bird.velocity = Vector2(0, 0)
        rb_pig.velocity = Vector2(0, 0)
        assert gm._all_stopped() is True

    def test_not_stopped_when_bird_moving(self):
        """If a bird has velocity above MIN_VELOCITY, _all_stopped returns False."""
        gm, rb_bird, rb_pig = self._make_gm_with_objects()
        rb_bird.velocity = Vector2(5, 0)  # sqr_magnitude = 25 >> MIN_VELOCITY
        rb_pig.velocity = Vector2(0, 0)
        assert gm._all_stopped() is False

    def test_not_stopped_when_pig_moving(self):
        """If a pig has velocity above MIN_VELOCITY, _all_stopped returns False."""
        gm, rb_bird, rb_pig = self._make_gm_with_objects()
        rb_bird.velocity = Vector2(0, 0)
        rb_pig.velocity = Vector2(0, 3)
        assert gm._all_stopped() is False

    def test_destroyed_objects_are_ignored(self):
        """Destroyed (inactive) objects should not block _all_stopped."""
        gm, rb_bird, rb_pig = self._make_gm_with_objects()
        # Destroy the pig -- it should be skipped
        pig_go = gm.pigs[0]
        GameObject.destroy(pig_go)
        rb_bird.velocity = Vector2(0, 0)
        assert gm._all_stopped() is True

    def test_min_velocity_threshold(self):
        """The threshold is Constants.MIN_VELOCITY (0.05) compared against sqr_magnitude."""
        assert Constants.MIN_VELOCITY == pytest.approx(0.05)
