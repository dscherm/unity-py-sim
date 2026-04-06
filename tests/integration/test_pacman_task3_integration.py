"""Integration tests for Pacman Task 3 — pellet collection through full scene.

Sets up the full Pacman scene and verifies pellet/GameManager behavior
via the actual engine lifecycle.
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
from src.engine.physics.physics_manager import PhysicsManager
from pacman_python.game_manager import GameManager
from pacman_python.pellet import Pellet
from pacman_python.power_pellet import PowerPellet


@pytest.fixture(autouse=True)
def clean_engine():
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager._instance = None
    GameManager.instance = None
    yield
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager._instance = None
    GameManager.instance = None


def _setup_scene():
    from run_pacman import setup_scene
    setup_scene()


class TestPacmanSceneSetup:

    def test_pellets_exist_with_pellet_tag(self):
        _setup_scene()
        pellets = GameObject.find_game_objects_with_tag("Pellet")
        assert len(pellets) > 0

    def test_power_pellets_exist_with_tag(self):
        _setup_scene()
        pps = GameObject.find_game_objects_with_tag("PowerPellet")
        assert len(pps) > 0

    def test_pacman_on_layer_7(self):
        _setup_scene()
        pac = GameObject.find_with_tag("Pacman")
        assert pac is not None
        assert pac.layer == 7

    def test_game_manager_singleton_set_after_awake(self):
        _setup_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        gm_go = GameObject.find("GameManager")
        assert gm_go is not None
        gm_comps = [c for c in gm_go._components if type(c).__name__ == "GameManager"]
        assert len(gm_comps) > 0
        assert type(gm_comps[0]).instance is gm_comps[0]

    def test_power_pellet_has_50_points(self):
        _setup_scene()
        pps = GameObject.find_game_objects_with_tag("PowerPellet")
        for go in pps:
            comps = [c for c in go._components if type(c).__name__ == "PowerPellet"]
            assert len(comps) > 0
            assert comps[0].points == 50


class TestPelletCollectionIntegration:

    def test_eating_pellet_increases_score(self):
        _setup_scene()
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        pac = GameObject.find_with_tag("Pacman")
        gm_go = GameObject.find("GameManager")
        gm_comps = [c for c in gm_go._components if type(c).__name__ == "GameManager"]
        gm = gm_comps[0]

        initial_score = gm.score
        target = GameObject.find_game_objects_with_tag("Pellet")[0]
        pellet_comps = [c for c in target._components
                        if type(c).__name__ in ("Pellet", "PowerPellet")]
        pc = pellet_comps[0]

        pc.on_trigger_enter_2d(pac)
        assert gm.score > initial_score
        assert target.active is False
