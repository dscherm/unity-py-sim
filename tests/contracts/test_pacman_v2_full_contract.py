"""Contract tests for Pacman V2 ghost system.

Tests verify behavioral contracts derived from the zigurous Unity Pacman tutorial:
- Ghost: aggregator with home/scatter/chase/frightened behaviors and reset_state
- GhostBehavior: base class with enable(duration)/disable() pattern
- GhostScatter: random direction at nodes, avoids reversing
- GhostChase: minimizes distance to target at nodes
- GhostFrightened: half speed, flee (maximize distance), eaten flag
- GhostHome: bounce on wall collision, exit transition coroutine
- GhostEyes: sprite swap based on movement direction
- GameManager: ghost_eaten multiplier doubling, power_pellet_eaten enables frightened
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "examples", "pacman_v2"))

from unittest.mock import MagicMock

from src.engine.core import GameObject
from src.engine.math.vector import Vector2

from pacman_v2_python.ghost import Ghost
from pacman_v2_python.ghost_scatter import GhostScatter
from pacman_v2_python.ghost_chase import GhostChase
from pacman_v2_python.ghost_frightened import GhostFrightened
from pacman_v2_python.ghost_home import GhostHome
from pacman_v2_python.ghost_eyes import GhostEyes
from pacman_v2_python.game_manager import GameManager
from pacman_v2_python.movement import Movement
from pacman_v2_python.node import Node
from pacman_v2_python.power_pellet import PowerPellet


# ── Helpers ──────────────────────────────────────────────────────

def make_ghost_go(name="TestGhost", position=None):
    """Build a ghost GameObject with all V2 components wired up (no physics).

    Uses _enabled to bypass on_enable/on_disable callbacks during setup,
    then calls awake() on behaviors to wire the ghost reference.
    """
    from src.engine.physics.rigidbody import Rigidbody2D

    go = GameObject(name)
    if position:
        go.transform.position = position

    rb = go.add_component(Rigidbody2D)
    mov = go.add_component(Movement)
    mov.speed = 7.0
    mov.initial_direction = Vector2(-1, 0)
    mov.rb = rb

    ghost = go.add_component(Ghost)

    home = go.add_component(GhostHome)
    home._enabled = False  # bypass callback

    scatter = go.add_component(GhostScatter)
    scatter.duration = 7.0
    scatter._enabled = False

    chase = go.add_component(GhostChase)
    chase.duration = 20.0
    chase._enabled = False

    frightened = go.add_component(GhostFrightened)
    frightened.duration = 8.0
    frightened._enabled = False

    # Call awake on behaviors to wire ghost reference
    ghost.awake()  # sets ghost.movement
    home.awake()   # sets home.ghost
    scatter.awake()
    chase.awake()
    frightened.awake()

    # Wire ghost references (normally done in start())
    ghost.movement = mov
    ghost.home = home
    ghost.scatter = scatter
    ghost.chase = chase
    ghost.frightened = frightened
    ghost.initial_behavior = scatter

    # Create target (Pacman stand-in)
    target_go = GameObject("Pacman")
    target_go.transform.position = Vector2(5, 5)
    ghost.target = target_go

    return go, ghost


def make_node(directions=None):
    """Build a mock node-like object with available_directions."""
    node_go = GameObject("Node")
    node = node_go.add_component(Node)
    node.available_directions = directions or [
        Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)
    ]
    return node_go


# ── Ghost contract tests ────────────────────────────────────────

class TestGhostContract:
    """Ghost aggregator must have references to all behavior components."""

    def test_ghost_has_behavior_slots(self):
        """Ghost class must declare home/scatter/chase/frightened/eyes slots."""
        go, ghost = make_ghost_go()
        assert hasattr(ghost, "home")
        assert hasattr(ghost, "scatter")
        assert hasattr(ghost, "chase")
        assert hasattr(ghost, "frightened")
        assert hasattr(ghost, "eyes")

    def test_ghost_has_movement_reference(self):
        go, ghost = make_ghost_go()
        assert ghost.movement is not None
        assert isinstance(ghost.movement, Movement)

    def test_ghost_reset_state_enables_scatter(self):
        """reset_state must enable scatter as default behavior cycle entry."""
        go, ghost = make_ghost_go()
        ghost.scatter.enabled = False
        ghost.reset_state()
        assert ghost.scatter.enabled is True

    def test_ghost_reset_state_disables_frightened(self):
        go, ghost = make_ghost_go()
        ghost.frightened.enabled = True
        ghost.reset_state()
        assert ghost.frightened.enabled is False

    def test_ghost_reset_state_disables_chase(self):
        go, ghost = make_ghost_go()
        ghost.chase.enabled = True
        ghost.reset_state()
        assert ghost.chase.enabled is False

    def test_ghost_reset_state_activates_game_object(self):
        go, ghost = make_ghost_go()
        go.active = False
        ghost.reset_state()
        assert go.active is True

    def test_ghost_reset_state_resets_movement(self):
        go, ghost = make_ghost_go()
        ghost.movement.speed_multiplier = 0.5
        ghost.reset_state()
        assert ghost.movement.speed_multiplier == 1.0

    def test_ghost_collision_frightened_calls_ghost_eaten(self):
        """When ghost is frightened and collides with Pacman, GameManager.ghost_eaten is called."""
        go, ghost = make_ghost_go()
        ghost.frightened.enabled = True
        ghost.frightened.eaten = False

        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        GameManager.instance = gm
        gm.ghost_eaten = MagicMock()

        # Use a real GameObject so getattr(collision, "game_object", collision)
        # falls through to the GO itself (GO has no .game_object attr)
        pacman_go = GameObject("PacCollider")
        pacman_go.layer = 3  # PACMAN_LAYER

        ghost.on_collision_enter_2d(pacman_go)
        gm.ghost_eaten.assert_called_once_with(ghost)
        GameManager.instance = None

    def test_ghost_collision_not_frightened_calls_pacman_eaten(self):
        """When ghost is NOT frightened and collides with Pacman, pacman_eaten is called."""
        go, ghost = make_ghost_go()
        ghost.frightened._enabled = False

        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        GameManager.instance = gm
        gm.pacman_eaten = MagicMock()

        pacman_go = GameObject("PacCollider")
        pacman_go.layer = 3

        ghost.on_collision_enter_2d(pacman_go)
        gm.pacman_eaten.assert_called_once()
        GameManager.instance = None

    def test_ghost_initial_behavior_home_for_house_ghosts(self):
        """Ghosts starting in the pen should have initial_behavior = home."""
        go, ghost = make_ghost_go()
        ghost.initial_behavior = ghost.home
        ghost.reset_state()
        assert ghost.home.enabled is True


# ── GhostBehavior contract tests ────────────────────────────────

class TestGhostBehaviorContract:
    """GhostBehavior enable/disable pattern matches Unity's zigurous pattern."""

    def test_enable_sets_enabled_true(self):
        go, ghost = make_ghost_go()
        ghost.scatter.enabled = False
        ghost.scatter.enable()
        assert ghost.scatter.enabled is True

    def test_disable_sets_enabled_false(self):
        go, ghost = make_ghost_go()
        ghost.scatter.enabled = True
        ghost.scatter.disable()
        assert ghost.scatter.enabled is False

    def test_enable_with_default_duration_uses_self_duration(self):
        """enable(-1) should use self.duration for the timed transition."""
        go, ghost = make_ghost_go()
        ghost.scatter.duration = 7.0
        ghost.scatter.invoke = MagicMock()
        ghost.scatter.cancel_invoke = MagicMock()
        ghost.scatter.enable()
        ghost.scatter.invoke.assert_called_with("disable", 7.0)

    def test_enable_with_explicit_duration(self):
        go, ghost = make_ghost_go()
        ghost.scatter.invoke = MagicMock()
        ghost.scatter.cancel_invoke = MagicMock()
        ghost.scatter.enable(duration=3.0)
        ghost.scatter.invoke.assert_called_with("disable", 3.0)

    def test_disable_cancels_invoke(self):
        go, ghost = make_ghost_go()
        ghost.scatter.cancel_invoke = MagicMock()
        ghost.scatter.disable()
        ghost.scatter.cancel_invoke.assert_called()

    def test_behavior_has_ghost_reference(self):
        """GhostBehavior.awake() should find Ghost on same GameObject."""
        go, ghost = make_ghost_go()
        assert ghost.scatter.ghost is ghost


# ── GhostScatter contract tests ─────────────────────────────────

class TestGhostScatterContract:
    """GhostScatter picks random direction at nodes, avoids reversing."""

    def test_scatter_on_disable_enables_chase(self):
        """When scatter timer expires, chase should be enabled."""
        go, ghost = make_ghost_go()
        ghost.chase.enabled = False
        ghost.scatter.on_disable()
        assert ghost.chase.enabled is True

    def test_scatter_avoids_reverse_direction(self):
        """Scatter must not pick the exact reverse of current movement direction."""
        go, ghost = make_ghost_go()
        ghost.movement.direction = Vector2(1, 0)

        node_go = make_node([Vector2(-1, 0), Vector2(0, 1)])

        ghost.scatter.enabled = True
        # Trigger multiple times to test probabilistically
        for _ in range(20):
            ghost.movement.set_direction = MagicMock()
            ghost.scatter.on_trigger_enter_2d(node_go)
            if ghost.movement.set_direction.called:
                chosen = ghost.movement.set_direction.call_args[0][0]
                # Should never pick (-1,0) which is reverse of (1,0)
                assert not (chosen.x == -1 and chosen.y == 0), \
                    "Scatter picked reverse direction"

    def test_scatter_ignores_non_node_objects(self):
        """Scatter should not act on collision with non-node objects."""
        go, ghost = make_ghost_go()
        ghost.scatter.enabled = True
        ghost.movement.set_direction = MagicMock()

        non_node_go = GameObject("Wall")
        ghost.scatter.on_trigger_enter_2d(non_node_go)
        ghost.movement.set_direction.assert_not_called()

    def test_scatter_skips_when_frightened(self):
        """Scatter yields to frightened mode — does not pick direction."""
        go, ghost = make_ghost_go()
        ghost.scatter.enabled = True
        ghost.frightened.enabled = True
        ghost.movement.set_direction = MagicMock()

        node_go = make_node()
        ghost.scatter.on_trigger_enter_2d(node_go)
        ghost.movement.set_direction.assert_not_called()


# ── GhostChase contract tests ───────────────────────────────────

class TestGhostChaseContract:
    """GhostChase picks direction minimizing distance to target."""

    def test_chase_on_disable_enables_scatter(self):
        go, ghost = make_ghost_go()
        ghost.scatter.enabled = False
        ghost.chase.on_disable()
        assert ghost.scatter.enabled is True

    def test_chase_picks_direction_toward_target(self):
        """Chase must pick direction that minimizes distance to target."""
        go, ghost = make_ghost_go()
        go.transform.position = Vector2(0, 0)
        ghost.target.transform.position = Vector2(5, 0)  # Target is to the right
        ghost.movement.direction = Vector2(0, 1)  # Currently moving up

        node_go = make_node([Vector2(1, 0), Vector2(0, 1), Vector2(0, -1)])

        ghost.chase.enabled = True
        ghost.movement.set_direction = MagicMock()
        ghost.chase.on_trigger_enter_2d(node_go)

        assert ghost.movement.set_direction.called
        chosen = ghost.movement.set_direction.call_args[0][0]
        assert chosen.x == 1 and chosen.y == 0, \
            f"Expected right (1,0) toward target, got ({chosen.x},{chosen.y})"

    def test_chase_avoids_reverse(self):
        """Chase must not reverse direction even if it's shortest."""
        go, ghost = make_ghost_go()
        go.transform.position = Vector2(0, 0)
        ghost.target.transform.position = Vector2(-5, 0)
        ghost.movement.direction = Vector2(1, 0)

        # Only options: reverse (-1,0) and up (0,1)
        node_go = make_node([Vector2(-1, 0), Vector2(0, 1)])

        ghost.chase.enabled = True
        ghost.movement.set_direction = MagicMock()
        ghost.chase.on_trigger_enter_2d(node_go)

        assert ghost.movement.set_direction.called
        chosen = ghost.movement.set_direction.call_args[0][0]
        # Should pick (0,1) because (-1,0) is reverse
        assert not (chosen.x == -1 and chosen.y == 0), "Chase reversed direction"

    def test_chase_skips_when_frightened(self):
        go, ghost = make_ghost_go()
        ghost.chase.enabled = True
        ghost.frightened.enabled = True
        ghost.movement.set_direction = MagicMock()

        node_go = make_node()
        ghost.chase.on_trigger_enter_2d(node_go)
        ghost.movement.set_direction.assert_not_called()


# ── GhostFrightened contract tests ──────────────────────────────

class TestGhostFrightenedContract:
    """GhostFrightened: half speed, flee behavior, eaten tracking."""

    def test_frightened_on_enable_sets_half_speed(self):
        go, ghost = make_ghost_go()
        ghost.movement.speed_multiplier = 1.0
        ghost.frightened.on_enable()
        assert ghost.frightened.ghost.movement.speed_multiplier == 0.5

    def test_frightened_on_disable_restores_speed(self):
        go, ghost = make_ghost_go()
        ghost.movement.speed_multiplier = 0.5
        ghost.frightened.on_disable()
        assert ghost.frightened.ghost.movement.speed_multiplier == 1.0

    def test_frightened_enable_resets_eaten(self):
        go, ghost = make_ghost_go()
        ghost.frightened.eaten = True
        ghost.frightened.enable(duration=5.0)
        assert ghost.frightened.eaten is False

    def test_frightened_disable_resets_eaten(self):
        go, ghost = make_ghost_go()
        ghost.frightened.eaten = True
        ghost.frightened.disable()
        assert ghost.frightened.eaten is False

    def test_frightened_flee_maximizes_distance(self):
        """Frightened mode should flee: pick direction maximizing distance from target."""
        go, ghost = make_ghost_go()
        go.transform.position = Vector2(0, 0)
        ghost.target.transform.position = Vector2(5, 0)  # Target to the right
        ghost.movement.direction = Vector2(0, 1)

        # Offer: left (away from target) and right (toward target)
        node_go = make_node([Vector2(-1, 0), Vector2(1, 0), Vector2(0, 1)])

        ghost.frightened.enabled = True
        ghost.movement.set_direction = MagicMock()
        ghost.frightened.on_trigger_enter_2d(node_go)

        assert ghost.movement.set_direction.called
        chosen = ghost.movement.set_direction.call_args[0][0]
        assert chosen.x == -1 and chosen.y == 0, \
            f"Frightened should flee left (-1,0), got ({chosen.x},{chosen.y})"

    def test_frightened_eat_sends_home_and_disables(self):
        """eat() must enable ghost home behavior and disable frightened.

        Note: eaten flag is set True then cleared by disable(), so after eat()
        eaten is False. The important contracts are: home enabled, frightened disabled.
        """
        go, ghost = make_ghost_go()

        # Create home inside point
        inside_go = GameObject("Inside")
        inside_go.transform.position = Vector2(0, 0)
        ghost.home.inside = inside_go

        ghost.frightened._enabled = True
        ghost.frightened.eat()
        assert ghost.home.enabled is True, "eat() must enable ghost home"
        assert ghost.frightened.enabled is False, "eat() must disable frightened"


# ── GhostHome contract tests ────────────────────────────────────

class TestGhostHomeContract:
    """GhostHome: bounce in pen and exit transition."""

    def test_home_bounce_reverses_direction_on_wall(self):
        """on_collision_enter_2d with obstacle layer reverses direction."""
        go, ghost = make_ghost_go()
        ghost.home._enabled = True
        ghost.movement.direction = Vector2(0, 1)

        # Use real GameObject for wall (MagicMock auto-creates .game_object attr)
        wall_go = GameObject("Wall")
        wall_go.layer = 6  # OBSTACLE_LAYER

        ghost.movement.set_direction = MagicMock()
        ghost.home.on_collision_enter_2d(wall_go)

        assert ghost.movement.set_direction.called
        args = ghost.movement.set_direction.call_args
        dir_arg = args[0][0]
        assert dir_arg.x == 0 and dir_arg.y == -1, "Should reverse from up to down"
        assert args[1].get("forced") is True, "Bounce must use forced=True"

    def test_home_bounce_only_when_enabled(self):
        go, ghost = make_ghost_go()
        ghost.home._enabled = False
        ghost.movement.set_direction = MagicMock()

        wall_go = GameObject("Wall2")
        wall_go.layer = 6

        ghost.home.on_collision_enter_2d(wall_go)
        ghost.movement.set_direction.assert_not_called()

    def test_home_on_disable_starts_exit_coroutine(self):
        """on_disable should start exit transition coroutine if ghost is active."""
        go, ghost = make_ghost_go()
        go.active = True
        ghost.home.start_coroutine = MagicMock()
        ghost.home.on_disable()
        ghost.home.start_coroutine.assert_called_once()


# ── GhostEyes contract tests ────────────────────────────────────

class TestGhostEyesContract:
    """GhostEyes swaps sprite based on movement direction."""

    def _make_eyes(self):
        """Build a ghost+eyes setup for testing."""
        from src.engine.rendering.renderer import SpriteRenderer

        ghost_go = GameObject("Ghost")
        mov = ghost_go.add_component(Movement)
        mov.direction = Vector2(1, 0)

        eyes_go = GameObject("Eyes")
        eyes_go.transform.set_parent(ghost_go.transform)

        sr = eyes_go.add_component(SpriteRenderer)
        eyes = eyes_go.add_component(GhostEyes)

        # Mock sprites
        eyes.sprite_up = "UP"
        eyes.sprite_down = "DOWN"
        eyes.sprite_left = "LEFT"
        eyes.sprite_right = "RIGHT"

        eyes._sprite_renderer = sr
        eyes._movement = mov
        eyes._parent_go = ghost_go

        return eyes, sr, mov, ghost_go

    def test_eyes_right(self):
        eyes, sr, mov, _ = self._make_eyes()
        mov.direction = Vector2(1, 0)
        eyes.update()
        assert sr.sprite == "RIGHT"

    def test_eyes_left(self):
        eyes, sr, mov, _ = self._make_eyes()
        mov.direction = Vector2(-1, 0)
        eyes.update()
        assert sr.sprite == "LEFT"

    def test_eyes_up(self):
        eyes, sr, mov, _ = self._make_eyes()
        mov.direction = Vector2(0, 1)
        eyes.update()
        assert sr.sprite == "UP"

    def test_eyes_down(self):
        eyes, sr, mov, _ = self._make_eyes()
        mov.direction = Vector2(0, -1)
        eyes.update()
        assert sr.sprite == "DOWN"

    def test_eyes_hidden_when_parent_inactive(self):
        eyes, sr, mov, ghost_go = self._make_eyes()
        sr.enabled = True
        ghost_go.active = False
        eyes.update()
        assert sr.enabled is False


# ── GameManager contract tests ──────────────────────────────────

class TestGameManagerContract:
    """GameManager scoring, multiplier, and state management."""

    def _make_gm(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        GameManager.instance = gm
        return gm

    def test_ghost_eaten_awards_points_with_multiplier(self):
        gm = self._make_gm()
        gm.score = 0
        gm.ghost_multiplier = 1

        go, ghost = make_ghost_go()
        ghost.points = 200

        # Mock frightened.eat so it doesn't try home transition
        ghost.frightened.eat = MagicMock()

        gm.ghost_eaten(ghost)
        assert gm.score == 200  # 200 * 1
        GameManager.instance = None

    def test_ghost_eaten_doubles_multiplier(self):
        gm = self._make_gm()
        gm.ghost_multiplier = 1
        go, ghost = make_ghost_go()
        ghost.frightened.eat = MagicMock()

        gm.ghost_eaten(ghost)
        assert gm.ghost_multiplier == 2

        gm.ghost_eaten(ghost)
        assert gm.ghost_multiplier == 3
        GameManager.instance = None

    def test_ghost_eaten_escalating_points(self):
        """Eating ghosts in sequence: 200, 400, 600, 800."""
        gm = self._make_gm()
        gm.score = 0
        gm.ghost_multiplier = 1
        go, ghost = make_ghost_go()
        ghost.points = 200
        ghost.frightened.eat = MagicMock()

        gm.ghost_eaten(ghost)
        assert gm.score == 200  # 200 * 1

        gm.ghost_eaten(ghost)
        assert gm.score == 600  # 200 + 200*2

        gm.ghost_eaten(ghost)
        assert gm.score == 1200  # 600 + 200*3

        gm.ghost_eaten(ghost)
        assert gm.score == 2000  # 1200 + 200*4
        GameManager.instance = None

    def test_power_pellet_enables_frightened_on_all_ghosts(self):
        gm = self._make_gm()
        go1, ghost1 = make_ghost_go("G1")
        go2, ghost2 = make_ghost_go("G2")
        ghost1.frightened.enable = MagicMock()
        ghost2.frightened.enable = MagicMock()
        gm.ghosts = [ghost1, ghost2]
        gm._all_pellets = []

        pp = MagicMock(spec=PowerPellet)
        pp.duration = 8.0
        pp.points = 50
        pp.game_object = MagicMock()
        pp.game_object.active = True

        gm.power_pellet_eaten(pp)
        ghost1.frightened.enable.assert_called_once_with(8.0)
        ghost2.frightened.enable.assert_called_once_with(8.0)
        GameManager.instance = None

    def test_power_pellet_resets_multiplier(self):
        gm = self._make_gm()
        gm.ghost_multiplier = 4
        gm.ghosts = []
        gm._all_pellets = []

        pp = MagicMock(spec=PowerPellet)
        pp.duration = 8.0
        pp.points = 50
        pp.game_object = MagicMock()
        pp.game_object.active = True

        gm.power_pellet_eaten(pp)
        assert gm.ghost_multiplier == 1
        GameManager.instance = None

    def test_pacman_eaten_decrements_lives(self):
        gm = self._make_gm()
        gm.lives = 3

        pacman_go = GameObject("Pacman")
        from pacman_v2_python.pacman import Pacman
        pac = pacman_go.add_component(Pacman)
        pac.death_sequence_start = MagicMock()
        gm.pacman = pac
        gm.ghosts = []

        gm.pacman_eaten()
        assert gm.lives == 2
        GameManager.instance = None

    def test_new_game_resets_score_and_lives(self):
        gm = self._make_gm()
        gm.score = 5000
        gm.lives = 0
        gm.ghosts = []
        gm._all_pellets = []

        # Mock pacman
        pacman_go = GameObject("Pacman")
        from pacman_v2_python.pacman import Pacman
        pac = pacman_go.add_component(Pacman)
        from pacman_v2_python.movement import Movement as Mov
        mov = pacman_go.add_component(Mov)
        pac.movement = mov
        gm.pacman = pac

        gm.new_game()
        assert gm.score == 0
        assert gm.lives == 3
        GameManager.instance = None
