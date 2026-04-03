"""GameManager — singleton controlling score, lives, rounds, game over.

Maps to: zigurous/GameManager.cs
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2
from src.engine.coroutine import WaitForSeconds
from src.engine.ui import Canvas, RectTransform, Text, TextAnchor


class GameManager(MonoBehaviour):

    _instance = None

    def __init__(self):
        super().__init__()
        self.score: int = 0
        self.lives: int = 3
        self._player = None
        self._invaders = None
        self._mystery_ship = None
        self._bunkers: list = []

    def awake(self):
        GameManager._instance = self

    def start(self):
        from space_invaders_python.player import Player
        from space_invaders_python.invaders import Invaders
        from space_invaders_python.mystery_ship import MysteryShip
        from space_invaders_python.bunker import Bunker

        # Find game objects
        player_go = GameObject.find("Player")
        if player_go:
            self._player = player_go.get_component(Player)

        invaders_go = GameObject.find("InvadersGrid")
        if invaders_go:
            self._invaders = invaders_go.get_component(Invaders)

        ship_go = GameObject.find("MysteryShip")
        if ship_go:
            self._mystery_ship = ship_go.get_component(MysteryShip)

        for go in GameObject.find_game_objects_with_tag("Bunker"):
            bunker = go.get_component(Bunker)
            if bunker:
                self._bunkers.append(bunker)

        self._setup_ui()
        self._new_game()

    def update(self):
        if self.lives <= 0:
            from src.engine.input_manager import Input
            if Input.get_key_down("return"):
                self._new_game()

    def _new_game(self):
        self._set_score(0)
        self._set_lives(3)
        self._new_round()

    def _new_round(self):
        if self._invaders:
            self._invaders.reset_invaders()
        for bunker in self._bunkers:
            bunker.reset_bunker()
            bunker.game_object.active = True
        self._respawn()

    def _respawn(self):
        if self._player:
            self._player.transform.position = Vector2(0, -5)
            self._player.game_object.active = True

    def _game_over(self):
        if hasattr(self, '_status_text'):
            self._status_text.text = "GAME OVER — Press Enter"

    def _set_score(self, score: int):
        self.score = score
        if hasattr(self, '_score_text'):
            self._score_text.text = f"Score: {str(score).zfill(4)}"
        self._update_title()

    def _set_lives(self, lives: int):
        self.lives = max(0, lives)
        if hasattr(self, '_lives_text'):
            self._lives_text.text = f"Lives: {self.lives}"
        self._update_title()

    def on_player_killed(self):
        self._set_lives(self.lives - 1)
        if self._player:
            self._player.game_object.active = False

        if self.lives > 0:
            self.start_coroutine(self._delayed_new_round())
        else:
            self._game_over()

    def _delayed_new_round(self):
        yield WaitForSeconds(1.0)
        self._new_round()

    def on_invader_killed(self, invader):
        invader.game_object.active = False
        self._set_score(self.score + invader.score)

        if self._invaders and self._invaders.get_alive_count() == 0:
            self._new_round()

    def on_mystery_ship_killed(self, ship):
        self._set_score(self.score + ship.score)

    def on_boundary_reached(self):
        if self._invaders:
            # Invaders reached bottom — immediate death
            self.on_player_killed()

    def _setup_ui(self):
        from src.engine.lifecycle import LifecycleManager
        lm = LifecycleManager.instance()

        canvas_go = GameObject("UICanvas")
        canvas = canvas_go.add_component(Canvas)
        lm.register_component(canvas)

        # Score (top left)
        score_go = GameObject("ScoreText")
        rt = score_go.add_component(RectTransform)
        rt.anchor_min = Vector2(0, 1)
        rt.anchor_max = Vector2(0, 1)
        rt.anchored_position = Vector2(80, -15)
        rt.size_delta = Vector2(200, 30)
        self._score_text = score_go.add_component(Text)
        self._score_text.text = "Score: 0000"
        self._score_text.font_size = 20
        self._score_text.color = (255, 255, 255)
        self._score_text.alignment = TextAnchor.UPPER_LEFT

        # Lives (top right)
        lives_go = GameObject("LivesText")
        rt2 = lives_go.add_component(RectTransform)
        rt2.anchor_min = Vector2(1, 1)
        rt2.anchor_max = Vector2(1, 1)
        rt2.anchored_position = Vector2(-80, -15)
        rt2.size_delta = Vector2(200, 30)
        self._lives_text = lives_go.add_component(Text)
        self._lives_text.text = "Lives: 3"
        self._lives_text.font_size = 20
        self._lives_text.color = (255, 255, 255)
        self._lives_text.alignment = TextAnchor.UPPER_RIGHT

        # Status (center)
        status_go = GameObject("StatusText")
        rt3 = status_go.add_component(RectTransform)
        rt3.anchor_min = Vector2(0.5, 0.5)
        rt3.anchor_max = Vector2(0.5, 0.5)
        rt3.anchored_position = Vector2(0, 0)
        rt3.size_delta = Vector2(400, 40)
        self._status_text = status_go.add_component(Text)
        self._status_text.text = ""
        self._status_text.font_size = 28
        self._status_text.color = (255, 255, 100)
        self._status_text.alignment = TextAnchor.MIDDLE_CENTER

    def _update_title(self):
        try:
            from src.engine.rendering.display import DisplayManager
            dm = DisplayManager.instance()
            dm._title = f"Space Invaders — Score: {self.score} | Lives: {self.lives}"
        except Exception:
            pass

    @staticmethod
    def reset():
        GameManager._instance = None
