from __future__ import annotations
"""GameManager — Flappy Bird game state manager.

Line-by-line translation of GameManager.cs from zigurous/unity-flappy-bird-tutorial.
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.time_manager import Time
from src.engine.ui import Text


class GameManager(MonoBehaviour):

    instance: 'GameManager | None' = None  # static GameManager Instance

    def __init__(self) -> None:
        super().__init__()
        self.player: MonoBehaviour | None = None          # [SerializeField] private Player player
        self.spawner: MonoBehaviour | None = None          # [SerializeField] private Spawner spawner
        self.score_text: Text | None = None                # [SerializeField] private Text scoreText
        self.play_button: GameObject | None = None         # [SerializeField] private GameObject playButton
        self.game_over_display: GameObject | None = None   # [SerializeField] private GameObject gameOver

        self.score: int = 0  # public int score { get; private set; } = 0 in C#

    def awake(self) -> None:
        if GameManager.instance is not None:
            GameObject.destroy_immediate(self.game_object)
        else:
            GameManager.instance = self

    def on_destroy(self) -> None:
        if GameManager.instance is self:
            GameManager.instance = None

    def start(self) -> None:
        self.pause()

    def pause(self) -> None:
        Time.set_time_scale(0.0)
        if self.player is not None:
            self.player.enabled = False

    def play(self) -> None:
        self.score = 0
        if self.score_text is not None:
            self.score_text.text = str(self.score)

        if self.play_button is not None:
            self.play_button.set_active(False)
        if self.game_over_display is not None:
            self.game_over_display.set_active(False)

        Time.set_time_scale(1.0)
        if self.player is not None:
            self.player.enabled = True

        from examples.flappy_bird.flappy_bird_python.pipes import Pipes
        pipes = GameObject.find_objects_of_type(Pipes)

        for i in range(len(pipes)):
            GameObject.destroy(pipes[i].game_object)

    def game_over(self) -> None:
        if self.play_button is not None:
            self.play_button.set_active(True)
        if self.game_over_display is not None:
            self.game_over_display.set_active(True)

        self.pause()

    def increase_score(self) -> None:
        self.score += 1
        if self.score_text is not None:
            self.score_text.text = str(self.score)
