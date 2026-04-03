"""GameManager — controls bird queue, turn flow, win/lose conditions."""

from src.engine.core import GameObject, MonoBehaviour
from src.engine.physics.rigidbody import Rigidbody2D
from src.engine.time_manager import Time
from src.engine.math.vector import Vector2
from src.engine.coroutine import WaitForSeconds

from .constants import Constants
from .enums import GameState, SlingshotState
from .slingshot import Slingshot


LEVEL_NAMES = ["level_1", "level_2"]


class GameManager(MonoBehaviour):

    _instance = None
    current_level_index = 0

    def __init__(self):
        super().__init__()
        self.game_state = GameState.START
        self.current_bird_index = 0
        self.birds: list[GameObject] = []
        self.pigs: list[GameObject] = []
        self.bricks: list[GameObject] = []
        self.slingshot: Slingshot | None = None
        self.score = 0

    @classmethod
    def reset(cls):
        cls._instance = None

    def start(self):
        GameManager._instance = self
        self.birds = list(GameObject.find_game_objects_with_tag("Bird"))
        self.pigs = list(GameObject.find_game_objects_with_tag("Pig"))
        self.bricks = list(GameObject.find_game_objects_with_tag("Brick"))

        sling_go = GameObject.find("Slingshot")
        if sling_go:
            self.slingshot = sling_go.get_component(Slingshot)

    def update(self):
        if self.game_state == GameState.START:
            self._handle_start()
        elif self.game_state == GameState.PLAYING:
            self._handle_playing()

        self._update_title()

    def _handle_start(self):
        from src.engine.input_manager import Input
        if Input.get_mouse_button_up(0):
            self._load_next_bird()
            self.game_state = GameState.PLAYING

    def _handle_playing(self):
        if self.slingshot is None:
            return

        if self.slingshot.slingshot_state == SlingshotState.BIRD_FLYING:
            # Check if everything has settled or timeout
            elapsed = Time.time - self.slingshot.time_since_thrown
            if self._all_stopped() or elapsed > Constants.SETTLE_TIMEOUT:
                self.start_coroutine(self._next_turn())

    def _next_turn(self):
        yield WaitForSeconds(1.0)

        if self._all_pigs_destroyed():
            self.score += 1000
            GameManager.current_level_index += 1
            if GameManager.current_level_index < len(LEVEL_NAMES):
                # Load next level
                from src.engine.scene import SceneManager
                SceneManager.load_scene(LEVEL_NAMES[GameManager.current_level_index])
            else:
                self.game_state = GameState.WON
            return

        self.current_bird_index += 1
        if self.current_bird_index >= len(self.birds):
            self.game_state = GameState.LOST
            return

        self._load_next_bird()
        self.slingshot.slingshot_state = SlingshotState.IDLE

    def _load_next_bird(self):
        if self.current_bird_index < len(self.birds):
            bird = self.birds[self.current_bird_index]
            if bird is not None and bird.active:
                if self.slingshot:
                    self.slingshot.bird_to_throw = bird
                    bird.transform.position = Vector2(
                        self.slingshot.slingshot_center.x,
                        self.slingshot.slingshot_center.y,
                    )

    def _all_stopped(self) -> bool:
        for obj in self.birds + self.pigs + self.bricks:
            if obj is None or not obj.active:
                continue
            rb = obj.get_component(Rigidbody2D)
            if rb and rb.velocity.sqr_magnitude > Constants.MIN_VELOCITY:
                return False
        return True

    def _all_pigs_destroyed(self) -> bool:
        return all(p is None or not p.active for p in self.pigs)

    def _update_title(self):
        try:
            from src.engine.rendering.display import DisplayManager
            dm = DisplayManager.instance()
            pigs_left = sum(1 for p in self.pigs if p is not None and p.active)
            birds_left = len(self.birds) - self.current_bird_index
            state = self.game_state.value
            dm._title = f"Angry Birds — {state} | Pigs: {pigs_left} | Birds: {birds_left} | Score: {self.score}"
        except Exception:
            pass
