"""Game manager — Python equivalent of GameManager.cs"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.time_manager import Time
from examples.pong.pong_python.ball_controller import BallController
from examples.pong.pong_python.score_manager import ScoreManager


class GameManager(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.reset_delay: float = 1.0
        self.ball: BallController | None = None
        self._is_resetting: bool = False
        self._reset_timer: float = 0.0

    def start(self):
        ball_obj = GameObject.find("Ball")
        self.ball = ball_obj.get_component(BallController)
        ScoreManager.reset_scores()

    def update(self):
        if self._is_resetting:
            self._reset_timer -= Time.delta_time
            if self._reset_timer <= 0:
                self._is_resetting = False
                self.ball.launch()

    def on_goal_scored(self, side: str):
        if side == "left":
            ScoreManager.add_score_right()
        else:
            ScoreManager.add_score_left()

        self.ball.reset()
        self._is_resetting = True
        self._reset_timer = self.reset_delay
