"""Mutation tests for Angry Birds gameplay systems.

Each test breaks a specific behavior via monkeypatch and asserts the break
changes observable output, proving the code depends on that logic path.
Expectations come from Unity's documented contracts, not from reading the impl.
"""

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
# Mutation 1: Brick damage formula uses divide instead of multiply
# ---------------------------------------------------------------------------
class TestMutationBrickDamageFormula:
    """Break the brick damage formula from magnitude * 10 to magnitude / 10.
    A hit that should kill the brick will instead do negligible damage."""

    def test_divide_instead_of_multiply_brick_survives(self, monkeypatch):
        """With damage = magnitude / 10 instead of * 10, a magnitude-8 hit
        deals only 0.8 damage instead of 80. Brick with 70 HP should survive."""
        go = GameObject("Brick", tag="Brick")
        rb = go.add_component(Rigidbody2D)
        rb.mass = 0.5
        sr = go.add_component(SpriteRenderer)
        sr.color = (180, 130, 70)
        sr.size = Vector2(1, 1)
        brick = go.add_component(Brick)
        brick.health = 70.0
        brick.max_health = 70.0

        # Broken on_collision_enter_2d: divide instead of multiply
        def broken_collision(self_brick, collision):
            other_rb = collision.game_object.get_component(Rigidbody2D)
            if other_rb is None:
                return
            damage = collision.relative_velocity.magnitude / 10  # BUG: / instead of *
            if damage < 5:
                return
            self_brick.health -= damage
            if self_brick.health <= 0:
                GameObject.destroy(self_brick.game_object)

        monkeypatch.setattr(Brick, "on_collision_enter_2d", broken_collision)

        other = GameObject("Hitter")
        other.add_component(Rigidbody2D)
        collision = Collision2D(
            game_object=other,
            relative_velocity=Vector2(8, 0),  # magnitude 8
        )
        brick.on_collision_enter_2d(collision)

        # With the mutation: damage = 8/10 = 0.8, which is < 5 threshold, so ignored
        assert go.active, "Mutant brick (divide) should survive a hit that should kill it"
        assert brick.health == pytest.approx(70.0), (
            "Mutant brick damage 0.8 < threshold 5, so health unchanged"
        )

        # Prove the real code kills it
        monkeypatch.undo()
        go2 = GameObject("Brick2", tag="Brick")
        go2.add_component(Rigidbody2D).mass = 0.5
        go2.add_component(SpriteRenderer).color = (180, 130, 70)
        go2.get_component(SpriteRenderer).size = Vector2(1, 1)
        brick2 = go2.add_component(Brick)
        brick2.health = 70.0
        brick2.max_health = 70.0

        other2 = GameObject("Hitter2")
        other2.add_component(Rigidbody2D)
        collision2 = Collision2D(
            game_object=other2,
            relative_velocity=Vector2(8, 0),
        )
        brick2.on_collision_enter_2d(collision2)
        assert not go2.active, "Real brick should be destroyed by magnitude-8 hit"


# ---------------------------------------------------------------------------
# Mutation 2: Pig instant-kill tag check removed
# ---------------------------------------------------------------------------
class TestMutationPigInstantKillRemoved:
    """Break pig by removing the Bird tag check. All collisions should now
    apply velocity-based damage instead of instant kill."""

    def test_pig_takes_damage_instead_of_dying(self, monkeypatch):
        """Without the tag check, a zero-velocity bird collision deals 0 damage
        and pig survives -- proving the tag check is essential."""
        go = GameObject("Pig", tag="Pig")
        go.add_component(Rigidbody2D).mass = 0.8
        pig = go.add_component(Pig)
        pig.health = 150.0

        # Broken: no tag check, always use damage formula
        def broken_collision(self_pig, collision):
            other_rb = collision.game_object.get_component(Rigidbody2D)
            if other_rb is None:
                return
            # Missing: if collision.game_object.tag == "Bird": destroy
            damage = collision.relative_velocity.magnitude * 10
            self_pig.health -= damage
            if self_pig.health <= 0:
                GameObject.destroy(self_pig.game_object)

        monkeypatch.setattr(Pig, "on_collision_enter_2d", broken_collision)

        bird = GameObject("Bird", tag="Bird")
        bird.add_component(Rigidbody2D)
        collision = Collision2D(
            game_object=bird,
            relative_velocity=Vector2(0, 0),  # zero velocity
        )
        pig.on_collision_enter_2d(collision)

        # With mutation: damage = 0, pig lives
        assert go.active, "Mutant pig (no tag check) should survive zero-velocity bird"
        assert pig.health == pytest.approx(150.0), "Mutant pig took 0 damage"

        # Prove the real code kills it
        monkeypatch.undo()
        go2 = GameObject("Pig2", tag="Pig")
        go2.add_component(Rigidbody2D).mass = 0.8
        pig2 = go2.add_component(Pig)
        pig2.health = 150.0

        bird2 = GameObject("Bird2", tag="Bird")
        bird2.add_component(Rigidbody2D)
        collision2 = Collision2D(
            game_object=bird2,
            relative_velocity=Vector2(0, 0),
        )
        pig2.on_collision_enter_2d(collision2)
        assert not go2.active, "Real pig should die instantly from Bird collision"


# ---------------------------------------------------------------------------
# Mutation 3: Destroyer tag filter broken (destroys everything)
# ---------------------------------------------------------------------------
class TestMutationDestroyerNoTagFilter:
    """Break the destroyer to destroy ALL entering objects regardless of tag.
    Non-tagged objects that should survive will be destroyed."""

    def test_untagged_object_destroyed_by_mutant(self, monkeypatch):
        """A Ground-tagged object should survive the real destroyer but die
        to the mutant that destroys everything."""
        dest_go = GameObject("Destroyer")
        destroyer = dest_go.add_component(Destroyer)

        # Broken: destroy everything, no tag check
        def broken_trigger(self_dest, other):
            GameObject.destroy(other)

        monkeypatch.setattr(Destroyer, "on_trigger_enter_2d", broken_trigger)

        ground = GameObject("Ground", tag="Ground")
        destroyer.on_trigger_enter_2d(ground)

        assert not ground.active, "Mutant destroyer should destroy Ground (no filter)"

        # Prove real code preserves it
        monkeypatch.undo()
        ground2 = GameObject("Ground2", tag="Ground")
        dest_go2 = GameObject("Destroyer2")
        dest2 = dest_go2.add_component(Destroyer)
        dest2.on_trigger_enter_2d(ground2)
        assert ground2.active, "Real destroyer should NOT destroy Ground-tagged objects"

    def test_mutant_also_kills_untagged(self, monkeypatch):
        """Untagged objects should also be destroyed by the mutant."""
        dest_go = GameObject("Destroyer")
        destroyer = dest_go.add_component(Destroyer)

        def broken_trigger(self_dest, other):
            GameObject.destroy(other)

        monkeypatch.setattr(Destroyer, "on_trigger_enter_2d", broken_trigger)

        random_obj = GameObject("Random", tag="Untagged")
        destroyer.on_trigger_enter_2d(random_obj)
        assert not random_obj.active, "Mutant should destroy Untagged objects"


# ---------------------------------------------------------------------------
# Mutation 4: GameManager._all_pigs_destroyed always returns False
# ---------------------------------------------------------------------------
class TestMutationAllPigsDestroyedAlwaysFalse:
    """Break _all_pigs_destroyed to always return False. The game should
    never reach GameState.WON even when all pigs are actually gone."""

    def test_game_never_wins(self, monkeypatch):
        """With _all_pigs_destroyed broken, the game transitions to LOST
        (no more birds) instead of WON."""
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

        # One bird
        bird_go = GameObject("Bird", tag="Bird")
        bird_go.transform.position = Vector2(-5, -3.5)
        rb_b = bird_go.add_component(Rigidbody2D)
        rb_b.mass = 1.0
        col_b = bird_go.add_component(CircleCollider2D)
        col_b.radius = 0.3
        col_b.build()
        bird_comp = bird_go.add_component(Bird)
        lm.register_component(bird_comp)
        sling.bird_to_throw = bird_go

        # One pig (will be destroyed)
        pig_go = GameObject("Pig", tag="Pig")
        pig_go.transform.position = Vector2(5, -3.7)
        pig_go.add_component(Rigidbody2D).mass = 0.8

        # GameManager
        gm_go = GameObject("GameManager")
        gm = gm_go.add_component(GameManager)
        GameManager.reset()
        lm.register_component(gm)

        lm.process_awake_queue()
        lm.process_start_queue()

        # Destroy the pig
        GameObject.destroy(pig_go)

        # Break _all_pigs_destroyed to always return False
        monkeypatch.setattr(GameManager, "_all_pigs_destroyed", lambda self: False)

        # Set level index past all levels (so if it somehow gets to the check, it would WON)
        from examples.angry_birds.angry_birds_python.game_manager import LEVEL_NAMES
        GameManager.current_level_index = len(LEVEL_NAMES)

        # Run the coroutine
        gen = gm._next_turn()
        wait = next(gen)  # WaitForSeconds(1.0)

        try:
            next(gen)
        except StopIteration:
            pass

        # With the mutation, it should go to the bird check path and find
        # current_bird_index (0) + 1 = 1 >= len(birds) (1), so LOST
        assert gm.game_state == GameState.LOST, (
            "With _all_pigs_destroyed broken (always False), game should reach LOST, not WON"
        )

    def test_real_code_reaches_won(self):
        """Prove the real code does reach WON when all pigs are destroyed."""
        lm = LifecycleManager.instance()

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
        bird_go.add_component(Rigidbody2D).mass = 1.0
        col_b = bird_go.add_component(CircleCollider2D)
        col_b.radius = 0.3
        col_b.build()
        bird_comp = bird_go.add_component(Bird)
        lm.register_component(bird_comp)
        sling.bird_to_throw = bird_go

        # Pig
        pig_go = GameObject("Pig", tag="Pig")
        pig_go.transform.position = Vector2(5, -3.7)
        pig_go.add_component(Rigidbody2D).mass = 0.8

        # GM
        gm_go = GameObject("GameManager")
        gm = gm_go.add_component(GameManager)
        GameManager.reset()
        lm.register_component(gm)

        lm.process_awake_queue()
        lm.process_start_queue()

        # Destroy pig, set level past end
        GameObject.destroy(pig_go)
        from examples.angry_birds.angry_birds_python.game_manager import LEVEL_NAMES
        GameManager.current_level_index = len(LEVEL_NAMES)

        gen = gm._next_turn()
        next(gen)  # WaitForSeconds
        try:
            next(gen)
        except StopIteration:
            pass

        assert gm.game_state == GameState.WON, "Real code should reach WON"
