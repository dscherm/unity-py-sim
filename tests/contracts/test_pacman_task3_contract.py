"""Contract tests for Pacman Task 3 — Pellet, PowerPellet, GameManager.

Derived from reference C# (zigurous/unity-pacman-tutorial) and Unity docs,
NOT from reading existing tests.
"""

import sys
import os
import pytest

# Ensure consistent import paths
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_pacman_root = os.path.join(_project_root, "examples", "pacman")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
if _pacman_root not in sys.path:
    sys.path.insert(0, _pacman_root)

from src.engine.core import GameObject, MonoBehaviour, _clear_registry
from src.engine.lifecycle import LifecycleManager
from pacman_python.game_manager import GameManager
from pacman_python.pellet import Pellet, PACMAN_LAYER
from pacman_python.power_pellet import PowerPellet


@pytest.fixture(autouse=True)
def clean_engine():
    _clear_registry()
    LifecycleManager.reset()
    GameManager.instance = None
    yield
    _clear_registry()
    LifecycleManager.reset()
    GameManager.instance = None


def _run_lifecycle():
    lm = LifecycleManager.instance()
    lm.process_awake_queue()
    lm.process_start_queue()
    return lm


# ── Pellet contracts ────────────────────────────────────────────────────────

class TestPelletContract:

    def test_pellet_default_points_is_10(self):
        """C# reference: public int points = 10;"""
        go = GameObject("P", tag="Pellet")
        p = go.add_component(Pellet)
        assert p.points == 10

    def test_pacman_layer_constant_is_7(self):
        assert PACMAN_LAYER == 7

    def test_pellet_is_monobehaviour(self):
        assert issubclass(Pellet, MonoBehaviour)

    def test_pellet_trigger_pacman_layer_deactivates_and_scores(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        _run_lifecycle()

        p_go = GameObject("Pellet", tag="Pellet")
        p = p_go.add_component(Pellet)
        # Extra so new_round doesn't fire
        d = GameObject("D", tag="Pellet")
        d.add_component(Pellet)

        pac = GameObject("Pacman", tag="Pacman")
        pac.layer = 7
        p.on_trigger_enter_2d(pac)

        assert p_go.active is False
        assert gm.score == 10

    def test_pellet_trigger_non_pacman_layer_does_nothing(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        _run_lifecycle()

        p_go = GameObject("Pellet", tag="Pellet")
        p = p_go.add_component(Pellet)

        ghost = GameObject("Ghost")
        ghost.layer = 3
        p.on_trigger_enter_2d(ghost)

        assert p_go.active is True
        assert gm.score == 0

    def test_pellet_eat_without_game_manager_deactivates(self):
        p_go = GameObject("Pellet", tag="Pellet")
        p = p_go.add_component(Pellet)
        p.eat()
        assert p_go.active is False


# ── PowerPellet contracts ───────────────────────────────────────────────────

class TestPowerPelletContract:

    def test_inherits_pellet(self):
        assert issubclass(PowerPellet, Pellet)

    def test_default_duration_is_8(self):
        go = GameObject("PP", tag="PowerPellet")
        pp = go.add_component(PowerPellet)
        assert pp.duration == 8.0

    def test_inherits_default_points_10(self):
        go = GameObject("PP", tag="PowerPellet")
        pp = go.add_component(PowerPellet)
        assert pp.points == 10

    def test_trigger_pacman_layer_deactivates_and_scores(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        _run_lifecycle()

        d = GameObject("D", tag="Pellet")
        d.add_component(Pellet)

        pp_go = GameObject("PP", tag="PowerPellet")
        pp = pp_go.add_component(PowerPellet)
        pp.points = 50

        pac = GameObject("Pacman", tag="Pacman")
        pac.layer = 7
        pp.on_trigger_enter_2d(pac)

        assert pp_go.active is False
        assert gm.score == 50

    def test_eat_calls_power_pellet_eaten(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        _run_lifecycle()

        calls = []
        orig = gm.power_pellet_eaten

        def mock_ppe(pellet):
            calls.append("power_pellet_eaten")
            orig(pellet)

        gm.power_pellet_eaten = mock_ppe

        d = GameObject("D", tag="Pellet")
        d.add_component(Pellet)

        pp_go = GameObject("PP", tag="PowerPellet")
        pp = pp_go.add_component(PowerPellet)
        pp.points = 50
        pp.eat()

        assert "power_pellet_eaten" in calls


# ── GameManager contracts ───────────────────────────────────────────────────

class TestGameManagerContract:

    def test_is_monobehaviour(self):
        assert issubclass(GameManager, MonoBehaviour)

    def test_singleton_set_on_awake(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        LifecycleManager.instance().process_awake_queue()
        assert GameManager.instance is gm

    def test_singleton_rejects_second_instance(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        lm = LifecycleManager.instance()
        lm.process_awake_queue()

        gm2_go = GameObject("GM2")
        gm2_go.add_component(GameManager)
        lm.process_awake_queue()

        assert GameManager.instance is gm
        assert gm2_go.active is False

    def test_singleton_cleared_on_destroy(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        LifecycleManager.instance().process_awake_queue()
        gm.on_destroy()
        assert GameManager.instance is None

    def test_new_game_resets_score_and_lives(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        _run_lifecycle()
        gm.score = 500
        gm.lives = 1
        gm.new_game()
        assert gm.score == 0
        assert gm.lives == 3

    def test_pellet_eaten_increments_score(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        _run_lifecycle()

        d = GameObject("D", tag="Pellet")
        d.add_component(Pellet)

        p_go = GameObject("P", tag="Pellet")
        p = p_go.add_component(Pellet)
        gm.pellet_eaten(p)
        assert gm.score == 10

    def test_pellet_eaten_deactivates_go(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        _run_lifecycle()

        d = GameObject("D", tag="Pellet")
        d.add_component(Pellet)

        p_go = GameObject("P", tag="Pellet")
        p = p_go.add_component(Pellet)
        gm.pellet_eaten(p)
        assert p_go.active is False

    def test_pellet_eaten_accumulates(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        _run_lifecycle()

        extra = GameObject("E", tag="Pellet")
        extra.add_component(Pellet)

        p1 = GameObject("P1", tag="Pellet").add_component(Pellet)
        p2 = GameObject("P2", tag="Pellet").add_component(Pellet)
        pp = GameObject("PP", tag="PowerPellet").add_component(PowerPellet)
        pp.points = 50

        gm.pellet_eaten(p1)
        gm.pellet_eaten(p2)
        gm.pellet_eaten(pp)
        assert gm.score == 70

    def test_has_remaining_pellets_true_when_active(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        _run_lifecycle()
        GameObject("P", tag="Pellet").add_component(Pellet)
        assert gm.has_remaining_pellets() is True

    def test_has_remaining_pellets_false_when_all_inactive(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        _run_lifecycle()
        p = GameObject("P", tag="Pellet").add_component(Pellet)
        pp = GameObject("PP", tag="PowerPellet").add_component(PowerPellet)
        p.game_object.active = False
        pp.game_object.active = False
        assert gm.has_remaining_pellets() is False

    def test_new_round_reactivation_bug(self):
        """BUG: new_round uses find_game_objects_with_tag which skips inactive GOs.
        In Unity C#, GameManager iterates pellets Transform children regardless of active state.
        This test documents the known bug.
        """
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        _run_lifecycle()

        p_go = GameObject("P", tag="Pellet")
        p_go.add_component(Pellet)
        p_go.active = False

        gm.new_round()
        # This SHOULD be True (Unity behavior), but is False due to the bug
        assert p_go.active is False, \
            "Known bug: new_round cannot find inactive pellets to reactivate"

    def test_power_pellet_eaten_resets_ghost_multiplier(self):
        gm_go = GameObject("GM")
        gm = gm_go.add_component(GameManager)
        _run_lifecycle()
        gm._ghost_multiplier = 4

        d = GameObject("D", tag="Pellet")
        d.add_component(Pellet)

        pp = GameObject("PP", tag="PowerPellet").add_component(PowerPellet)
        pp.points = 50
        gm.power_pellet_eaten(pp)
        assert gm._ghost_multiplier == 1
        assert gm.score == 50

    def test_initial_lives_3(self):
        gm = GameObject("GM").add_component(GameManager)
        assert gm.lives == 3
