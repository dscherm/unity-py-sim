"""Mutation tests for Pacman Task 3 — monkeypatch breakage to prove tests catch bugs.

Each test introduces a specific mutation (simulating a developer mistake)
and verifies the system behaves incorrectly in the expected way,
proving the real code is correctly tested.
"""

import sys
import os
import pytest

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_pacman_root = os.path.join(_project_root, "examples", "pacman")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
if _pacman_root not in sys.path:
    sys.path.insert(0, _pacman_root)

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from pacman_python.game_manager import GameManager
from pacman_python.pellet import Pellet
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


class TestMutationPelletLayerCheck:

    def test_broken_layer_check_allows_ghosts(self, monkeypatch):
        """Remove layer check: any GO triggers eat."""
        gm = GameObject("GM").add_component(GameManager)
        _run_lifecycle()

        d = GameObject("D", tag="Pellet")
        d.add_component(Pellet)
        p_go = GameObject("P", tag="Pellet")
        p = p_go.add_component(Pellet)

        ghost = GameObject("Ghost")
        ghost.layer = 3

        monkeypatch.setattr(Pellet, "on_trigger_enter_2d",
                            lambda self, other: self.eat())

        p.on_trigger_enter_2d(ghost)
        assert p_go.active is False, "Mutant allows ghost to eat pellet"

    def test_real_layer_check_blocks_ghosts(self):
        """Real code: non-Pacman layer is ignored."""
        gm = GameObject("GM").add_component(GameManager)
        _run_lifecycle()

        d = GameObject("D", tag="Pellet")
        d.add_component(Pellet)
        p_go = GameObject("P", tag="Pellet")
        p = p_go.add_component(Pellet)

        ghost = GameObject("Ghost")
        ghost.layer = 3
        p.on_trigger_enter_2d(ghost)

        assert p_go.active is True


class TestMutationPelletEatenNoDeactivate:

    def test_broken_deactivate(self, monkeypatch):
        """Mutant: pellet_eaten doesn't deactivate the pellet GO."""
        gm = GameObject("GM").add_component(GameManager)
        _run_lifecycle()

        d = GameObject("D", tag="Pellet")
        d.add_component(Pellet)
        p_go = GameObject("P", tag="Pellet")
        p = p_go.add_component(Pellet)

        def broken(self, pellet):
            self.score += pellet.points
            self._update_title()

        monkeypatch.setattr(GameManager, "pellet_eaten", broken)

        pac = GameObject("Pac", tag="Pacman")
        pac.layer = 7
        p.on_trigger_enter_2d(pac)

        assert p_go.active is True, "Mutant leaves pellet active"

    def test_real_deactivates(self):
        """Real code: pellet_eaten deactivates the pellet."""
        gm = GameObject("GM").add_component(GameManager)
        _run_lifecycle()

        d = GameObject("D", tag="Pellet")
        d.add_component(Pellet)
        p_go = GameObject("P", tag="Pellet")
        p = p_go.add_component(Pellet)

        pac = GameObject("Pac", tag="Pacman")
        pac.layer = 7
        p.on_trigger_enter_2d(pac)

        assert p_go.active is False


class TestMutationHasRemainingAlwaysTrue:

    def test_broken_always_true(self, monkeypatch):
        """Mutant: has_remaining_pellets always True prevents new_round."""
        gm = GameObject("GM").add_component(GameManager)
        _run_lifecycle()

        d = GameObject("D", tag="Pellet")
        d.add_component(Pellet)
        p = GameObject("P", tag="Pellet").add_component(Pellet)

        monkeypatch.setattr(GameManager, "has_remaining_pellets", lambda self: True)

        pac = GameObject("Pac", tag="Pacman")
        pac.layer = 7
        gm.pellet_eaten(p)

        # Score incremented, but new_round never fires (even if last pellet)
        assert gm.score == 10


class TestMutationPowerPelletWrongMethod:

    def test_broken_eat_skips_multiplier_reset(self, monkeypatch):
        """Mutant: PowerPellet.eat calls pellet_eaten directly (skips ghost multiplier reset)."""
        gm = GameObject("GM").add_component(GameManager)
        _run_lifecycle()
        gm._ghost_multiplier = 4

        d = GameObject("D", tag="Pellet")
        d.add_component(Pellet)
        pp = GameObject("PP", tag="PowerPellet").add_component(PowerPellet)
        pp.points = 50

        def broken_eat(self):
            if GameManager.instance is not None:
                GameManager.instance.pellet_eaten(self)
            else:
                self.game_object.active = False

        monkeypatch.setattr(PowerPellet, "eat", broken_eat)

        pac = GameObject("Pac", tag="Pacman")
        pac.layer = 7
        pp.on_trigger_enter_2d(pac)

        assert gm._ghost_multiplier == 4, "Mutant doesn't reset multiplier"

    def test_real_eat_resets_multiplier(self):
        """Real code: power_pellet_eaten resets ghost multiplier."""
        gm = GameObject("GM").add_component(GameManager)
        _run_lifecycle()
        gm._ghost_multiplier = 4

        d = GameObject("D", tag="Pellet")
        d.add_component(Pellet)
        pp = GameObject("PP", tag="PowerPellet").add_component(PowerPellet)
        pp.points = 50

        pac = GameObject("Pac", tag="Pacman")
        pac.layer = 7
        pp.on_trigger_enter_2d(pac)

        assert gm._ghost_multiplier == 1
