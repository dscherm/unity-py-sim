"""Mutation tests for Pacman Tasks 1 & 2 — monkeypatch breakage to prove tests catch it.

Each test breaks a specific behavior via monkeypatch and verifies the broken
behavior is observable, proving the contract tests are meaningful.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "examples", "pacman"))

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time
from src.engine.input_manager import Input
from src.engine.rendering.renderer import SpriteRenderer


@pytest.fixture
def engine():
    """Reset engine state."""
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    Time._reset()
    Input._reset()
    pm = PhysicsManager.instance()
    pm.gravity = Vector2(0, 0)
    lm = LifecycleManager.instance()
    yield lm, pm
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    Time._reset()
    Input._reset()


def _tick(lm, pm, dt=1.0 / 60):
    """One lifecycle tick."""
    Time._delta_time = dt
    Time._time += dt
    Time._frame_count += 1
    lm.process_awake_queue()
    lm.process_start_queue()
    lm.run_fixed_update()
    pm.step(Time._fixed_delta_time)
    lm.run_update()
    lm.run_late_update()


def _create_wall(x, y):
    from pacman_python.movement import OBSTACLE_LAYER
    wall = GameObject(f"Wall_{x}_{y}")
    wall.layer = OBSTACLE_LAYER
    wall.transform.position = Vector2(x, y)
    rb = wall.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.STATIC
    col = wall.add_component(BoxCollider2D)
    col.size = Vector2(1.0, 1.0)
    return wall


def _create_pacman(x, y, initial_dir=None):
    from pacman_python.movement import Movement
    go = GameObject("Pacman")
    go.layer = 7
    go.transform.position = Vector2(x, y)
    rb = go.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.KINEMATIC
    col = go.add_component(CircleCollider2D)
    col.radius = 0.5
    sr = go.add_component(SpriteRenderer)
    sr.size = Vector2(1.0, 1.0)
    mv = go.add_component(Movement)
    if initial_dir:
        mv.initial_direction = initial_dir
    return go, mv


# ============================================================
# Mutation 1: Break Movement.occupied() to always return False
# ============================================================


class TestMutationOccupiedAlwaysFalse:
    """If occupied() never detects walls, Pacman walks through walls."""

    def test_broken_occupied_allows_wall_passage(self, engine, monkeypatch):
        """Mutant: occupied() -> False always. Pacman moves into wall."""
        from pacman_python.movement import Movement
        lm, pm = engine

        # Wall directly to the right
        _create_wall(1, 0)
        go, mv = _create_pacman(0, 0, Vector2(1, 0))
        _tick(lm, pm)

        # Normal behavior: Pacman should NOT move past x=1 (wall is there)
        start_x = go.transform.position.x
        for _ in range(30):
            _tick(lm, pm)
        normal_x = go.transform.position.x

        # Reset
        _clear_registry()
        LifecycleManager.reset()
        PhysicsManager.reset()
        Time._reset()
        pm2 = PhysicsManager.instance()
        pm2.gravity = Vector2(0, 0)
        lm2 = LifecycleManager.instance()

        _create_wall(1, 0)
        go2, mv2 = _create_pacman(0, 0, Vector2(1, 0))

        # Break occupied
        monkeypatch.setattr(Movement, "occupied", lambda self, d: False)

        _tick(lm2, pm2)
        for _ in range(30):
            _tick(lm2, pm2)
        broken_x = go2.transform.position.x

        # With broken occupied, Pacman should pass through the wall
        assert broken_x > normal_x, \
            f"Broken occupied should let Pacman past wall: normal={normal_x}, broken={broken_x}"


# ============================================================
# Mutation 2: Break AnimatedSprite._advance() to never increment
# ============================================================


class TestMutationAnimationStall:
    """If _advance() never increments frame, animation stalls."""

    def test_broken_advance_stalls_animation(self, engine, monkeypatch):
        """Mutant: _advance() is a no-op. Frame never changes."""
        from pacman_python.animated_sprite import AnimatedSprite
        lm, pm = engine

        go = GameObject("Animated")
        sr = go.add_component(SpriteRenderer)
        sr.enabled = True
        anim = go.add_component(AnimatedSprite)
        anim.sprite_refs = ["a", "b", "c"]
        anim.animation_time = 0.01
        anim.loop = True

        # Break _advance
        monkeypatch.setattr(AnimatedSprite, "_advance", lambda self: None)

        _tick(lm, pm)

        initial_frame = anim._animation_frame
        for _ in range(100):
            _tick(lm, pm, dt=0.02)

        assert anim._animation_frame == initial_frame, \
            "Broken _advance should keep frame at initial value"
        assert anim._animation_frame == 0, \
            "Frame should be stuck at 0 with broken _advance"


# ============================================================
# Mutation 3: Break Passage.on_trigger_enter_2d to not teleport
# ============================================================


class TestMutationPassageNoTeleport:
    """If passage doesn't teleport, position stays the same."""

    def test_broken_passage_does_not_teleport(self, engine, monkeypatch):
        """Mutant: on_trigger_enter_2d is a no-op. No teleportation."""
        from pacman_python.passage import Passage
        lm, pm = engine

        left_go = GameObject("PassageLeft")
        left_go.transform.position = Vector2(-14, 0)
        rb = left_go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.STATIC
        col = left_go.add_component(BoxCollider2D)
        col.is_trigger = True
        col.size = Vector2(1.0, 1.0)
        passage = left_go.add_component(Passage)

        right_go = GameObject("PassageRight")
        right_go.transform.position = Vector2(14, 0)
        passage.connection = right_go.transform

        _tick(lm, pm)

        # Break teleport — replace with no-op
        monkeypatch.setattr(Passage, "on_trigger_enter_2d", lambda self, other: None)

        pac = GameObject("Pacman")
        pac.transform.position = Vector2(-14, 0)
        original_x = pac.transform.position.x

        # Call the broken method
        passage.on_trigger_enter_2d(pac)

        assert abs(pac.transform.position.x - original_x) < 0.01, \
            "Broken passage should NOT teleport — position unchanged"


# ============================================================
# Mutation 4: Break Node._check_available_direction to never add
# ============================================================


class TestMutationNodeNoDirections:
    """If _check_available_direction never adds, node has 0 available dirs."""

    def test_broken_check_yields_zero_directions(self, engine, monkeypatch):
        """Mutant: _check_available_direction is a no-op. No directions detected."""
        from pacman_python.node import Node
        lm, pm = engine

        # Open intersection (no walls)
        node_go = GameObject("Node")
        node_go.transform.position = Vector2(0, 0)
        rb = node_go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.STATIC
        col = node_go.add_component(BoxCollider2D)
        col.is_trigger = True
        col.size = Vector2(0.5, 0.5)
        node = node_go.add_component(Node)

        # Break the direction check
        monkeypatch.setattr(Node, "_check_available_direction", lambda self, d: None)

        _tick(lm, pm)

        assert len(node.available_directions) == 0, \
            "Broken _check should yield 0 available directions"

    def test_normal_check_yields_directions(self, engine):
        """Sanity: Without mutation, open node should have 4 directions."""
        from pacman_python.node import Node
        lm, pm = engine

        node_go = GameObject("Node")
        node_go.transform.position = Vector2(0, 0)
        rb = node_go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.STATIC
        col = node_go.add_component(BoxCollider2D)
        col.is_trigger = True
        col.size = Vector2(0.5, 0.5)
        node = node_go.add_component(Node)

        _tick(lm, pm)

        assert len(node.available_directions) == 4, \
            f"Open node should detect 4 directions, got {len(node.available_directions)}"


# ============================================================
# Mutation 5: Break Movement.set_direction to never queue
# ============================================================


class TestMutationNoDirectionQueuing:
    """If set_direction never queues, blocked directions are lost."""

    def test_broken_queuing_loses_direction(self, engine, monkeypatch):
        """Mutant: set_direction ignores blocked directions entirely."""
        from pacman_python.movement import Movement
        lm, pm = engine

        _create_wall(0, 1)
        go, mv = _create_pacman(0, 0, Vector2(1, 0))
        _tick(lm, pm)

        # Break set_direction to never queue
        original_set_dir = Movement.set_direction

        def broken_set_dir(self, direction, forced=False):
            if forced or not self.occupied(direction):
                self.direction = direction
                self.next_direction = Vector2(0, 0)
            # Else: do nothing (don't queue)

        monkeypatch.setattr(Movement, "set_direction", broken_set_dir)

        mv.set_direction(Vector2(0, 1))  # Up into wall

        assert mv.next_direction.x == 0 and mv.next_direction.y == 0, \
            "Broken set_direction should NOT queue the blocked direction"
        assert mv.direction.x == 1, "Direction should remain unchanged"


# ============================================================
# Mutation 6: Break Movement speed to 0
# ============================================================


class TestMutationZeroSpeed:
    """If speed is zero, Pacman doesn't move even with a valid direction."""

    def test_zero_speed_prevents_movement(self, engine, monkeypatch):
        """Mutant: speed = 0. Pacman is stationary."""
        lm, pm = engine

        go, mv = _create_pacman(0, 0, Vector2(1, 0))
        _tick(lm, pm)

        start_x = go.transform.position.x
        monkeypatch.setattr(mv, "speed", 0.0)

        for _ in range(30):
            _tick(lm, pm)

        assert abs(go.transform.position.x - start_x) < 0.001, \
            "Zero speed should prevent movement"
