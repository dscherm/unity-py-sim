"""Run Angry Birds in the Python Unity simulator.

Controls:
  Click to start
  Click + drag bird to aim slingshot
  Release to launch
  ESC: Quit
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.core import GameObject, MonoBehaviour
from src.engine.lifecycle import LifecycleManager
from src.engine.input_manager import Input
from src.engine.debug import Debug
from src.engine.app import run

from angry_birds_python.levels import register_all_levels, setup_level_1
from angry_birds_python.game_manager import GameManager


class QuitHandler(MonoBehaviour):
    def update(self):
        if Input.get_key_down("escape"):
            from src.engine.rendering.display import DisplayManager
            DisplayManager.instance().request_quit()
        Debug.tick(0.016)


def setup_scene():
    from src.engine.scene import SceneManager
    register_all_levels()
    GameManager.current_level_index = 0

    # Load level 1, then add quit handler
    setup_level_1()

    lm = LifecycleManager.instance()
    quit_go = GameObject("QuitHandler")
    qh = quit_go.add_component(QuitHandler)
    lm.register_component(qh)


if __name__ == "__main__":
    headless = "--headless" in sys.argv
    max_frames = None
    if "--frames" in sys.argv:
        idx = sys.argv.index("--frames")
        max_frames = int(sys.argv[idx + 1])

    print("Angry Birds — Click to start, drag bird to aim, release to launch, ESC to quit")
    run(setup_scene, width=900, height=600, headless=headless, max_frames=max_frames,
        title="Angry Birds — Click to Start")
