"""Ghost — central controller aggregating all ghost behaviors.

Port of zigurous Ghost.cs. Holds references to home/scatter/chase/frightened.
Handles collision with Pacman (eat or be eaten).

Lesson applied: Awake runs regardless of enabled state.
Lesson applied: component auto-registration (no manual register calls).
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2

from .movement import Movement
from .ghost_home import GhostHome
from .ghost_scatter import GhostScatter
from .ghost_chase import GhostChase
from .ghost_frightened import GhostFrightened
from .ghost_eyes import GhostEyes


PACMAN_LAYER: int = 3


class Ghost(MonoBehaviour):
    movement: Movement | None = None
    home: GhostHome | None = None
    scatter: GhostScatter | None = None
    chase: GhostChase | None = None
    frightened: GhostFrightened | None = None
    eyes: GhostEyes | None = None

    initial_behavior: str = "scatter"  # "home" or "scatter"
    target: GameObject | None = None   # What this ghost chases (usually Pacman)
    points: int = 200

    def awake(self) -> None:
        self.movement = self.get_component(Movement)
        self.home = self.get_component(GhostHome)
        self.scatter = self.get_component(GhostScatter)
        self.chase = self.get_component(GhostChase)
        self.frightened = self.get_component(GhostFrightened)

        # Set ghost reference on all behaviors
        for behavior in [self.home, self.scatter, self.chase, self.frightened]:
            if behavior:
                behavior.ghost = self

        # Find eyes on child object
        for child in self.transform.children:
            eyes = child.game_object.get_component(GhostEyes)
            if eyes:
                self.eyes = eyes
                break

    def reset_state(self) -> None:
        self.game_object.active = True
        if self.movement:
            self.movement.reset_state()

        # Disable all behaviors first
        for behavior in [self.home, self.scatter, self.chase, self.frightened]:
            if behavior:
                behavior.disable()

        # Enable initial behavior
        if self.initial_behavior == "home" and self.home:
            self.home.enable(0)
        elif self.scatter:
            self.scatter.enable(self.scatter.duration)

    def on_collision_enter_2d(self, collision) -> None:
        other_go = getattr(collision, "game_object", collision)
        if other_go.layer == PACMAN_LAYER:
            if self.frightened and self.frightened.enabled and not self.frightened.eaten:
                # Ghost is eaten by Pacman
                from .game_manager import GameManager
                if GameManager.instance:
                    GameManager.instance.ghost_eaten(self)
            else:
                # Pacman is eaten by ghost
                from .game_manager import GameManager
                if GameManager.instance:
                    GameManager.instance.pacman_eaten()
