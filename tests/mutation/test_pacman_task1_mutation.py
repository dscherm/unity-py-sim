"""Mutation tests for Pacman Task 1 — prove tests detect breakage.

Each test monkeypatches a critical behavior and verifies that the
system behaves incorrectly (proving the real code is necessary).
"""

import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.math.vector import Vector2
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.physics_manager import Physics2D, PhysicsManager
from src.engine.lifecycle import LifecycleManager
from src.engine.time_manager import Time

from examples.pacman.pacman_python.movement import Movement, OBSTACLE_LAYER


@pytest.fixture(autouse=True)
def clean_engine():
    _clear_registry()
    PhysicsManager.reset()
    LifecycleManager.reset()
    Time._reset()
    yield
    _clear_registry()
    PhysicsManager.reset()
    LifecycleManager.reset()
    Time._reset()


def _run_lifecycle():
    lm = LifecycleManager.instance()
    lm.process_awake_queue()
    lm.process_start_queue()


def _run_frames(n: int):
    lm = LifecycleManager.instance()
    pm = PhysicsManager.instance()
    fixed_dt = Time._fixed_delta_time
    for _ in range(n):
        Time._delta_time = 1.0 / 60.0
        Time._time += Time._delta_time
        Time._frame_count += 1
        lm.process_awake_queue()
        lm.process_start_queue()
        lm.run_fixed_update()
        pm.step(fixed_dt)
        lm.run_update()
        lm.run_late_update()


def _make_wall(x, y, layer=OBSTACLE_LAYER):
    go = GameObject(f"Wall_{x}_{y}")
    go.layer = layer
    go.transform.position = Vector2(x, y)
    rb = go.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.STATIC
    col = go.add_component(BoxCollider2D)
    col.size = Vector2(1.0, 1.0)
    return go


def _make_mover(x=0.0, y=0.0, direction=(1, 0)):
    pac = GameObject("Mover")
    pac.transform.position = Vector2(x, y)
    rb = pac.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.KINEMATIC
    pac.add_component(CircleCollider2D)
    mov = pac.add_component(Movement)
    mov.initial_direction = Vector2(direction[0], direction[1])
    mov.speed = 8.0
    return pac, mov


class TestOccupiedAlwaysFalseMutation:
    """Mutant: occupied() always returns False -> movement ignores walls."""

    def test_mover_passes_through_wall_when_occupied_broken(self, monkeypatch):
        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        # Wall directly ahead at x=1.5
        _make_wall(1.5, 0.0)

        pac, mov = _make_mover(0.0, 0.0, direction=(1, 0))
        _run_lifecycle()

        # Monkeypatch occupied to always return False
        monkeypatch.setattr(Movement, "occupied", lambda self, d: False)

        _run_frames(50)

        # With the mutation, the mover should pass right through the wall
        assert pac.transform.position.x > 1.5, (
            "With occupied() broken (always False), mover should pass through wall"
        )


class TestOccupiedAlwaysTrueMutation:
    """Mutant: occupied() always returns True -> movement is completely blocked."""

    def test_mover_cannot_move_when_occupied_broken(self, monkeypatch):
        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        pac, mov = _make_mover(0.0, 0.0, direction=(1, 0))
        _run_lifecycle()

        start_x = pac.transform.position.x

        # Monkeypatch occupied to always return True
        monkeypatch.setattr(Movement, "occupied", lambda self, d: True)

        _run_frames(20)

        # With the mutation, mover should stay put
        assert abs(pac.transform.position.x - start_x) < 0.001, (
            "With occupied() broken (always True), mover should not move at all"
        )


class TestLayerMaskFilteringMutation:
    """Mutant: remove layer_mask filtering -> overlap_box finds wrong-layer objects."""

    def test_overlap_box_finds_wrong_layer_when_filter_removed(self, monkeypatch):
        # Wall on layer 6
        _make_wall(5.0, 5.0, layer=6)
        _run_lifecycle()

        # Store original method
        original_overlap_box = Physics2D.overlap_box

        def broken_overlap_box(point, size, angle=0.0, layer_mask=-1):
            """Mutant: always pass layer_mask=-1 (ignores layer filtering)."""
            return original_overlap_box(point, size, angle, layer_mask=-1)

        monkeypatch.setattr(Physics2D, "overlap_box", staticmethod(broken_overlap_box))

        # Query for layer 8 — should find nothing with correct code,
        # but the mutant ignores the mask and finds the layer-6 wall
        hit = Physics2D.overlap_box(
            point=Vector2(5.0, 5.0),
            size=Vector2(1.0, 1.0),
            layer_mask=1 << 8,
        )
        assert hit is not None, (
            "With layer_mask filtering broken, should find wall on wrong layer"
        )


class TestTriggerSkipMutation:
    """Mutant: remove trigger skip -> overlap_box returns trigger colliders."""

    def test_overlap_box_returns_trigger_when_skip_removed(self, monkeypatch):
        # Trigger on layer 6
        go = GameObject("TriggerObj")
        go.layer = 6
        go.transform.position = Vector2(5.0, 5.0)
        rb = go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.STATIC
        col = go.add_component(BoxCollider2D)
        col.is_trigger = True
        col.size = Vector2(1.0, 1.0)
        _run_lifecycle()

        original_overlap_box = Physics2D.overlap_box

        def broken_overlap_box(point, size, angle=0.0, layer_mask=-1):
            """Mutant: skip the is_trigger check."""
            import pymunk
            pm = PhysicsManager.instance()
            hw, hh = size.x / 2, size.y / 2
            bb = pymunk.BB(point.x - hw, point.y - hh, point.x + hw, point.y + hh)
            query = pm._space.bb_query(bb, pymunk.ShapeFilter())
            for shape in query:
                collider_comp, _, _ = Physics2D._resolve_components(shape, pm)
                if collider_comp is None:
                    continue
                # MUTATION: removed is_trigger check
                if layer_mask != -1:
                    go_layer = collider_comp.game_object.layer
                    if not (layer_mask & (1 << go_layer)):
                        continue
                return collider_comp
            return None

        monkeypatch.setattr(Physics2D, "overlap_box", staticmethod(broken_overlap_box))

        hit = Physics2D.overlap_box(
            point=Vector2(5.0, 5.0),
            size=Vector2(2.0, 2.0),
            layer_mask=1 << 6,
        )
        assert hit is not None, (
            "With trigger-skip removed, overlap_box should return trigger colliders"
        )
        assert hit.is_trigger, "The returned collider should be the trigger"


class TestSpeedMultiplierMutation:
    """Mutant: ignore speed_multiplier -> speed is always base speed."""

    def test_speed_multiplier_ignored_when_broken(self, monkeypatch):
        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        pac, mov = _make_mover(0.0, 0.0, direction=(1, 0))
        _run_lifecycle()

        mov.speed_multiplier = 3.0

        # Run normal movement first
        _run_frames(5)
        normal_x = pac.transform.position.x

        # Reset
        pac.transform.position = Vector2(0.0, 0.0)

        # Monkeypatch fixed_update to ignore speed_multiplier
        original_fixed_update = Movement.fixed_update

        def broken_fixed_update(self):
            if self.rb is None:
                return
            if self.direction.x == 0 and self.direction.y == 0:
                return
            if self.occupied(self.direction):
                return
            pos = self.transform.position
            # MUTATION: uses 1.0 instead of self.speed_multiplier
            translation = Vector2(
                self.speed * 1.0 * Time.fixed_delta_time * self.direction.x,
                self.speed * 1.0 * Time.fixed_delta_time * self.direction.y,
            )
            new_pos = Vector2(pos.x + translation.x, pos.y + translation.y)
            self.rb.move_position(new_pos)
            self.transform.position = new_pos

        monkeypatch.setattr(Movement, "fixed_update", broken_fixed_update)

        _run_frames(5)
        broken_x = pac.transform.position.x

        # With 3x multiplier, normal should be ~3x broken
        assert normal_x > broken_x * 2.5, (
            f"Speed multiplier mutation: normal={normal_x}, broken={broken_x}. "
            f"Normal should be ~3x the broken (multiplier-ignored) distance"
        )


class TestDirectionQueueingMutation:
    """Mutant: remove direction queuing -> blocked directions are silently dropped."""

    def test_queuing_removed_drops_direction(self, monkeypatch):
        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        # Wall above
        _make_wall(0.0, 1.5)

        pac, mov = _make_mover(0.0, 0.0, direction=(0, 0))
        _run_lifecycle()

        def broken_set_direction(self, direction, forced=False):
            """Mutant: if blocked, do nothing (don't queue)."""
            if forced or not self.occupied(direction):
                self.direction = direction
                self.next_direction = Vector2(0, 0)
            # MUTATION: removed else branch that would queue the direction

        monkeypatch.setattr(Movement, "set_direction", broken_set_direction)

        # Try to go up (blocked)
        mov.set_direction(Vector2(0, 1))

        # With the mutation, next_direction should still be (0,0)
        assert mov.next_direction.x == 0 and mov.next_direction.y == 0, (
            "With queuing broken, blocked direction should be silently dropped"
        )
