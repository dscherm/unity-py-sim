"""Game manager — tracks score, lives, and game state."""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2
from src.engine.ui import Canvas, RectTransform, Text, TextAnchor


class GameManager(MonoBehaviour):

    score: int = 0
    lives: int = 3
    game_over: bool = False
    game_won: bool = False
    _instance = None

    def start(self):
        GameManager._instance = self
        self._setup_ui()

    @staticmethod
    def _get_instance():
        return GameManager._instance

    @staticmethod
    def reset():
        GameManager.score = 0
        GameManager.lives = 3
        GameManager.game_over = False
        GameManager.game_won = False
        GameManager._instance = None

    @staticmethod
    def add_score(points: int):
        GameManager.score += points
        GameManager._update_display()

    @staticmethod
    def on_ball_lost():
        if GameManager.game_over or GameManager.game_won:
            return
        GameManager.lives -= 1
        if GameManager.lives <= 0:
            GameManager.game_over = True
            print("Game Over!")
        GameManager._update_display()

    @staticmethod
    def on_brick_destroyed():
        # Check win condition — count remaining bricks
        remaining = GameObject.find_game_objects_with_tag("Brick")
        active = [go for go in remaining if go.active]
        if len(active) <= 0:
            GameManager.game_won = True
            print("You Win!")

    def _setup_ui(self):
        """Create UI canvas with score and lives text."""
        canvas_go = GameObject("UICanvas")
        self._canvas = canvas_go.add_component(Canvas)

        # Score text (top left)
        score_go = GameObject("ScoreText")
        rt_score = score_go.add_component(RectTransform)
        rt_score.anchor_min = Vector2(0.0, 1.0)
        rt_score.anchor_max = Vector2(0.0, 1.0)
        rt_score.anchored_position = Vector2(100, -20)
        rt_score.size_delta = Vector2(200, 30)
        self._score_text = score_go.add_component(Text)
        self._score_text.text = "Score: 0"
        self._score_text.font_size = 20
        self._score_text.color = (255, 255, 200)
        self._score_text.alignment = TextAnchor.UPPER_LEFT

        # Lives text (top right)
        lives_go = GameObject("LivesText")
        rt_lives = lives_go.add_component(RectTransform)
        rt_lives.anchor_min = Vector2(1.0, 1.0)
        rt_lives.anchor_max = Vector2(1.0, 1.0)
        rt_lives.anchored_position = Vector2(-100, -20)
        rt_lives.size_delta = Vector2(200, 30)
        self._lives_text = lives_go.add_component(Text)
        self._lives_text.text = "Lives: 3"
        self._lives_text.font_size = 20
        self._lives_text.color = (255, 200, 200)
        self._lives_text.alignment = TextAnchor.UPPER_RIGHT

        # Status text (top center)
        status_go = GameObject("StatusText")
        rt_status = status_go.add_component(RectTransform)
        rt_status.anchor_min = Vector2(0.5, 1.0)
        rt_status.anchor_max = Vector2(0.5, 1.0)
        rt_status.anchored_position = Vector2(0, -20)
        rt_status.size_delta = Vector2(300, 30)
        self._status_text = status_go.add_component(Text)
        self._status_text.text = "Space to Launch"
        self._status_text.font_size = 22
        self._status_text.color = (255, 255, 255)
        self._status_text.alignment = TextAnchor.UPPER_CENTER

    @staticmethod
    def _update_display():
        inst = GameManager._instance
        if inst and hasattr(inst, '_score_text'):
            inst._score_text.text = f"Score: {GameManager.score}"
            inst._lives_text.text = f"Lives: {GameManager.lives}"
            if GameManager.game_over:
                inst._status_text.text = "Game Over!"
            elif GameManager.game_won:
                inst._status_text.text = "You Win!"
            else:
                inst._status_text.text = ""
        # Also update window title as fallback
        try:
            from src.engine.rendering.display import DisplayManager
            dm = DisplayManager.instance()
            dm._title = (
                f"Breakout — Score: {GameManager.score}  |  Lives: {GameManager.lives}"
            )
        except Exception:
            pass
