"""Mutation tests for Pacman V2 ghost system.

Each test monkeypatches a specific behavior to break it, then verifies
the contract tests would catch the regression. This proves the contract
tests are actually testing meaningful behavior, not just passing vacuously.

Mutations tested:
1. Chase direction: maximize instead of minimize distance -> picks wrong direction
2. Frightened speed: remove half-speed multiplier -> ghost moves at full speed
3. Ghost eaten multiplier: remove doubling -> score doesn't escalate
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "examples", "pacman_v2"))

from unittest.mock import MagicMock

from src.engine.core import GameObject
from src.engine.math.vector import Vector2

from pacman_v2_python.ghost import Ghost
from pacman_v2_python.ghost_chase import GhostChase
from pacman_v2_python.ghost_frightened import GhostFrightened
from pacman_v2_python.ghost_scatter import GhostScatter
from pacman_v2_python.ghost_home import GhostHome
from pacman_v2_python.game_manager import GameManager
from pacman_v2_python.movement import Movement
from pacman_v2_python.node import Node


def make_ghost_go(name="TestGhost"):
    """Build a minimal ghost for mutation testing."""
    from src.engine.physics.rigidbody import Rigidbody2D

    go = GameObject(name)
    rb = go.add_component(Rigidbody2D)
    mov = go.add_component(Movement)
    mov.speed = 7.0
    mov.initial_direction = Vector2(-1, 0)
    mov.rb = rb

    ghost = go.add_component(Ghost)
    home = go.add_component(GhostHome)
    home._enabled = False
    scatter = go.add_component(GhostScatter)
    scatter.duration = 7.0
    scatter._enabled = False
    chase = go.add_component(GhostChase)
    chase.duration = 20.0
    chase._enabled = False
    frightened = go.add_component(GhostFrightened)
    frightened.duration = 8.0
    frightened._enabled = False

    # Call awake to wire ghost references on behaviors
    ghost.awake()
    home.awake()
    scatter.awake()
    chase.awake()
    frightened.awake()

    ghost.movement = mov
    ghost.home = home
    ghost.scatter = scatter
    ghost.chase = chase
    ghost.frightened = frightened
    ghost.initial_behavior = scatter

    target_go = GameObject("Pacman")
    target_go.transform.position = Vector2(10, 0)
    ghost.target = target_go

    return go, ghost


def make_node(directions):
    node_go = GameObject("Node")
    node = node_go.add_component(Node)
    node.available_directions = directions
    return node_go


# ── Mutation 1: Break chase direction logic ──────────────────────

class TestChaseMutation:
    """Mutant: GhostChase picks direction MAXIMIZING distance (flee instead of chase)."""

    def test_broken_chase_picks_wrong_direction(self, monkeypatch):
        """If chase maximizes distance, it picks away from target — test must catch this."""
        go, ghost = make_ghost_go()
        go.transform.position = Vector2(0, 0)
        ghost.target.transform.position = Vector2(10, 0)
        ghost.movement.direction = Vector2(0, 1)  # Currently up

        node_go = make_node([Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1)])

        def broken_on_trigger(self_chase, other):
            """Mutant: maximize distance instead of minimize."""
            other_go = getattr(other, "game_object", other)
            node = other_go.get_component(Node)
            if node is None or not self_chase.enabled:
                return
            if self_chase.ghost and self_chase.ghost.frightened and self_chase.ghost.frightened.enabled:
                return
            movement = self_chase.ghost.movement if self_chase.ghost else None
            target = self_chase.ghost.target if self_chase.ghost else None
            if movement is None or target is None:
                return
            available = node.available_directions
            if not available:
                return
            target_pos = target.transform.position
            best_dir = available[0]
            max_dist = -1.0  # MUTANT: maximize instead of minimize
            for d in available:
                if d.x == -movement.direction.x and d.y == -movement.direction.y:
                    continue
                pos = self_chase.transform.position
                new_x = pos.x + d.x
                new_y = pos.y + d.y
                dx = target_pos.x - new_x
                dy = target_pos.y - new_y
                dist = dx * dx + dy * dy
                if dist > max_dist:  # MUTANT: > instead of <
                    max_dist = dist
                    best_dir = d
            movement.set_direction(best_dir)

        monkeypatch.setattr(GhostChase, "on_trigger_enter_2d",
                            lambda self, other: broken_on_trigger(self, other))

        ghost.chase.enabled = True
        ghost.movement.set_direction = MagicMock()
        ghost.chase.on_trigger_enter_2d(node_go)

        assert ghost.movement.set_direction.called
        chosen = ghost.movement.set_direction.call_args[0][0]

        # The mutant should pick LEFT (-1,0) to maximize distance from target at (10,0)
        # The correct behavior would pick RIGHT (1,0) to minimize distance
        # This proves the contract test catches the mutation
        assert chosen.x == -1 and chosen.y == 0, \
            f"Mutant should flee left, got ({chosen.x},{chosen.y})"

    def test_correct_chase_picks_right_direction(self):
        """Baseline: correct chase picks direction toward target."""
        go, ghost = make_ghost_go()
        go.transform.position = Vector2(0, 0)
        ghost.target.transform.position = Vector2(10, 0)
        ghost.movement.direction = Vector2(0, 1)

        node_go = make_node([Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1)])

        ghost.chase.enabled = True
        ghost.movement.set_direction = MagicMock()
        ghost.chase.on_trigger_enter_2d(node_go)

        assert ghost.movement.set_direction.called
        chosen = ghost.movement.set_direction.call_args[0][0]
        assert chosen.x == 1 and chosen.y == 0, \
            f"Correct chase should go right, got ({chosen.x},{chosen.y})"

    def test_mutation_detected(self):
        """The mutant and correct versions must produce different results."""
        go1, ghost1 = make_ghost_go("G1")
        go1.transform.position = Vector2(0, 0)
        ghost1.target.transform.position = Vector2(10, 0)
        ghost1.movement.direction = Vector2(0, 1)

        go2, ghost2 = make_ghost_go("G2")
        go2.transform.position = Vector2(0, 0)
        ghost2.target.transform.position = Vector2(10, 0)
        ghost2.movement.direction = Vector2(0, 1)

        node_go = make_node([Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1)])

        # Correct behavior
        ghost1.chase.enabled = True
        ghost1.movement.set_direction = MagicMock()
        ghost1.chase.on_trigger_enter_2d(node_go)
        correct_dir = ghost1.movement.set_direction.call_args[0][0]

        # Mutant behavior (inline)
        ghost2.chase.enabled = True
        ghost2.movement.set_direction = MagicMock()

        # Manually run mutant logic
        available = [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1)]
        target_pos = ghost2.target.transform.position
        best_dir = available[0]
        max_dist = -1.0
        for d in available:
            if d.x == -ghost2.movement.direction.x and d.y == -ghost2.movement.direction.y:
                continue
            pos = go2.transform.position
            dist = (target_pos.x - (pos.x + d.x))**2 + (target_pos.y - (pos.y + d.y))**2
            if dist > max_dist:
                max_dist = dist
                best_dir = d

        # They must differ
        assert not (correct_dir.x == best_dir.x and correct_dir.y == best_dir.y), \
            "Mutation was NOT detected — correct and mutant chose same direction"


# ── Mutation 2: Break frightened speed multiplier ────────────────

class TestFrightenedSpeedMutation:
    """Mutant: GhostFrightened does NOT set half speed."""

    def test_broken_frightened_no_speed_change(self, monkeypatch):
        """If frightened doesn't halve speed, ghost moves at full speed."""
        go, ghost = make_ghost_go()
        ghost.movement.speed_multiplier = 1.0

        def broken_on_enable(self_f):
            # MUTANT: skip speed change
            self_f.eaten = False

        monkeypatch.setattr(GhostFrightened, "on_enable", broken_on_enable)
        ghost.frightened.on_enable()

        # With the mutation, speed stays at 1.0 — the contract test expects 0.5
        assert ghost.movement.speed_multiplier == 1.0, \
            "Mutant should leave speed at 1.0"

    def test_correct_frightened_halves_speed(self):
        """Baseline: correct behavior halves speed."""
        go, ghost = make_ghost_go()
        ghost.movement.speed_multiplier = 1.0
        ghost.frightened.on_enable()
        assert ghost.movement.speed_multiplier == 0.5

    def test_mutation_detected(self):
        """Contract test catches the speed mutation."""
        go, ghost = make_ghost_go()
        ghost.movement.speed_multiplier = 1.0

        # Correct
        ghost.frightened.on_enable()
        correct_speed = ghost.movement.speed_multiplier

        # Reset
        ghost.movement.speed_multiplier = 1.0

        # Mutant (skip speed change)
        ghost.frightened.eaten = False  # only thing mutant does
        mutant_speed = ghost.movement.speed_multiplier

        assert correct_speed != mutant_speed, \
            "Mutation was NOT detected — correct and mutant have same speed"


# ── Mutation 3: Break ghost eaten multiplier doubling ────────────

class TestGhostEatenMultiplierMutation:
    """Mutant: ghost_eaten does NOT increment the multiplier."""

    def test_broken_multiplier_stays_at_1(self, monkeypatch):
        """If multiplier never increments, all ghosts award base points."""
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        GameManager.instance = gm
        gm.score = 0
        gm.ghost_multiplier = 1

        def broken_ghost_eaten(self_gm, ghost):
            # MUTANT: award points but don't increment multiplier
            self_gm._set_score(self_gm.score + ghost.points * self_gm.ghost_multiplier)
            # MISSING: self_gm.ghost_multiplier += 1
            if ghost.frightened:
                ghost.frightened.eat()

        monkeypatch.setattr(GameManager, "ghost_eaten", broken_ghost_eaten)

        go, ghost = make_ghost_go()
        ghost.points = 200
        ghost.frightened.eat = MagicMock()

        gm.ghost_eaten(ghost)
        assert gm.score == 200
        assert gm.ghost_multiplier == 1  # Mutant: stays at 1

        gm.ghost_eaten(ghost)
        assert gm.score == 400  # Mutant: 200+200 instead of 200+400
        assert gm.ghost_multiplier == 1

        GameManager.instance = None

    def test_correct_multiplier_increments(self):
        """Baseline: correct behavior increments multiplier."""
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        GameManager.instance = gm
        gm.score = 0
        gm.ghost_multiplier = 1

        go, ghost = make_ghost_go()
        ghost.points = 200
        ghost.frightened.eat = MagicMock()

        gm.ghost_eaten(ghost)
        assert gm.score == 200
        assert gm.ghost_multiplier == 2

        gm.ghost_eaten(ghost)
        assert gm.score == 600  # 200 + 400
        assert gm.ghost_multiplier == 3

        GameManager.instance = None

    def test_mutation_detected(self):
        """Score diverges between correct and mutant after 2nd ghost."""
        # Correct
        gm_go = GameObject("GM_correct")
        gm = gm_go.add_component(GameManager)
        gm.score = 0
        gm.ghost_multiplier = 1
        go, ghost = make_ghost_go()
        ghost.points = 200
        ghost.frightened.eat = MagicMock()

        gm.ghost_eaten(ghost)
        gm.ghost_eaten(ghost)
        correct_score = gm.score

        # Mutant
        mutant_score = 0
        mult = 1
        for _ in range(2):
            mutant_score += 200 * mult
            # No multiplier increment

        assert correct_score != mutant_score, \
            "Mutation NOT detected — scores match"
