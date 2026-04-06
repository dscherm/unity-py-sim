"""Ghost — aggregates all ghost behaviors and handles Pacman collision.

Line-by-line port of Ghost.cs from zigurous/unity-pacman-tutorial.
"""

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2
from src.engine.rendering.renderer import SpriteRenderer
from pacman_python.movement import Movement


PACMAN_LAYER: int = 7


class Ghost(MonoBehaviour):
    movement: Movement | None = None
    home: object = None       # GhostHome
    scatter: object = None    # GhostScatter
    chase: object = None      # GhostChase
    frightened: object = None # GhostFrightened
    initial_behavior: object = None  # Which behavior to start with
    target: object = None     # Transform of Pacman (chase target)
    points: int = 200

    def awake(self) -> None:
        self.movement = self.get_component(Movement)

    def start(self) -> None:
        from pacman_python.ghost_home import GhostHome
        from pacman_python.ghost_scatter import GhostScatter
        from pacman_python.ghost_chase import GhostChase
        from pacman_python.ghost_frightened import GhostFrightened

        self.home = self.get_component(GhostHome)
        self.scatter = self.get_component(GhostScatter)
        self.chase = self.get_component(GhostChase)
        self.frightened = self.get_component(GhostFrightened)
        self.reset_state()

    def reset_state(self) -> None:
        self.game_object.active = True
        self.movement.reset_state()

        self.frightened.disable_behavior()
        self.chase.disable_behavior()
        self.scatter.enable_behavior()

        if self.home is not self.initial_behavior:
            self.home.disable_behavior()

        if self.initial_behavior is not None:
            self.initial_behavior.enable_behavior()

    def set_position(self, position: Vector2) -> None:
        self.transform.position = position

    def on_collision_enter_2d(self, collision) -> None:
        go = getattr(collision, 'game_object', collision)
        if go is not None and go.layer == PACMAN_LAYER:
            from pacman_python.game_manager import GameManager
            if GameManager.instance is not None:
                if self.frightened.enabled:
                    GameManager.instance.ghost_eaten(self)
                else:
                    GameManager.instance.pacman_eaten()
