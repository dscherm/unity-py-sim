"""GameManager — controls bird queue, turn flow, win/lose conditions."""

from src.engine.core import GameObject, MonoBehaviour
from src.engine.physics.rigidbody import Rigidbody2D
from src.engine.time_manager import Time
from src.engine.math.vector import Vector2
from src.engine.coroutine import WaitForSeconds
from src.engine.ui import Canvas, RectTransform, Text, TextAnchor

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

        self._setup_ui()

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

    def _setup_ui(self):
        """Create UI canvas with status and score text."""
        canvas_go = GameObject("UICanvas")
        self._canvas = canvas_go.add_component(Canvas)

        # Status text (top center)
        status_go = GameObject("StatusText")
        rt_status = status_go.add_component(RectTransform)
        rt_status.anchor_min = Vector2(0.5, 1.0)
        rt_status.anchor_max = Vector2(0.5, 1.0)
        rt_status.anchored_position = Vector2(0, -20)
        rt_status.size_delta = Vector2(400, 40)
        self._status_text = status_go.add_component(Text)
        self._status_text.text = "Click to Start"
        self._status_text.font_size = 24
        self._status_text.color = (255, 255, 255)
        self._status_text.alignment = TextAnchor.UPPER_CENTER

        # Score text (top right)
        score_go = GameObject("ScoreText")
        rt_score = score_go.add_component(RectTransform)
        rt_score.anchor_min = Vector2(1.0, 1.0)
        rt_score.anchor_max = Vector2(1.0, 1.0)
        rt_score.anchored_position = Vector2(-100, -20)
        rt_score.size_delta = Vector2(200, 30)
        self._score_text = score_go.add_component(Text)
        self._score_text.text = "Score: 0"
        self._score_text.font_size = 18
        self._score_text.color = (255, 255, 200)
        self._score_text.alignment = TextAnchor.UPPER_RIGHT

        # Birds remaining (top left)
        birds_go = GameObject("BirdsText")
        rt_birds = birds_go.add_component(RectTransform)
        rt_birds.anchor_min = Vector2(0.0, 1.0)
        rt_birds.anchor_max = Vector2(0.0, 1.0)
        rt_birds.anchored_position = Vector2(100, -20)
        rt_birds.size_delta = Vector2(200, 30)
        self._birds_text = birds_go.add_component(Text)
        self._birds_text.font_size = 18
        self._birds_text.color = (255, 200, 200)
        self._birds_text.alignment = TextAnchor.UPPER_LEFT

    def _update_title(self):
        pigs_left = sum(1 for p in self.pigs if p is not None and p.active)
        birds_left = len(self.birds) - self.current_bird_index

        if hasattr(self, '_status_text'):
            if self.game_state == GameState.START:
                self._status_text.text = "Click to Start"
            elif self.game_state == GameState.PLAYING:
                self._status_text.text = f"Pigs: {pigs_left}"
            elif self.game_state == GameState.WON:
                self._status_text.text = "You Win!"
            elif self.game_state == GameState.LOST:
                self._status_text.text = "You Lost!"

        if hasattr(self, '_score_text'):
            self._score_text.text = f"Score: {self.score}"

        if hasattr(self, '_birds_text'):
            self._birds_text.text = f"Birds: {birds_left}"

        # Also update window title as fallback
        try:
            from src.engine.rendering.display import DisplayManager
            dm = DisplayManager.instance()
            state = self.game_state.value
            dm._title = f"Angry Birds — {state} | Pigs: {pigs_left} | Birds: {birds_left} | Score: {self.score}"
        except Exception:
            pass
