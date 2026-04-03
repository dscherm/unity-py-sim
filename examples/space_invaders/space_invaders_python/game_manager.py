"""GameManager — singleton controlling score, lives, rounds, game over.

Line-by-line port of: zigurous/GameManager.cs
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.coroutine import WaitForSeconds
from src.engine.ui import Canvas, RectTransform, Text, TextAnchor
from src.engine.math.mathf import Mathf


class GameManager(MonoBehaviour):
    """[DefaultExecutionOrder(-1)]"""

    # public static GameManager Instance { get; private set; }
    instance = None

    def __init__(self):
        super().__init__()
        # [SerializeField] private GameObject gameOverUI
        self.game_over_ui: GameObject | None = None
        # [SerializeField] private Text scoreText
        self.score_text: Text | None = None
        # [SerializeField] private Text livesText
        self.lives_text: Text | None = None

        # private references
        self.player = None       # Player
        self.invaders = None     # Invaders
        self.mystery_ship = None # MysteryShip
        self.bunkers: list = []  # Bunker[]

        # public int score { get; private set; } = 0
        self.score: int = 0
        # public int lives { get; private set; } = 3
        self.lives: int = 3

        # Invoke timer for delayed calls
        self._invoke_callback = None
        self._invoke_timer: float = 0.0
        self._invoke_pending: bool = False

    def awake(self):
        # if (Instance != null) DestroyImmediate(gameObject)
        # else Instance = this
        if GameManager.instance is not None:
            self.game_object.active = False
        else:
            GameManager.instance = self

    def on_destroy(self):
        # if (Instance == this) Instance = null
        if GameManager.instance is self:
            GameManager.instance = None

    def start(self):
        # player = FindObjectOfType<Player>()
        from space_invaders_python.player import Player
        from space_invaders_python.invaders import Invaders
        from space_invaders_python.mystery_ship import MysteryShip
        from space_invaders_python.bunker import Bunker

        player_go = GameObject.find("Player")
        if player_go:
            self.player = player_go.get_component(Player)

        invaders_go = GameObject.find("InvadersGrid")
        if invaders_go:
            self.invaders = invaders_go.get_component(Invaders)

        ship_go = GameObject.find("MysteryShip")
        if ship_go:
            self.mystery_ship = ship_go.get_component(MysteryShip)

        # bunkers = FindObjectsOfType<Bunker>()
        for go in GameObject.find_game_objects_with_tag("Bunker"):
            bunker = go.get_component(Bunker)
            if bunker:
                self.bunkers.append(bunker)

        self._setup_ui()
        self._new_game()

    def update(self):
        # Invoke timer
        if self._invoke_pending:
            self._invoke_timer += Time.delta_time
            if self._invoke_timer >= self._invoke_delay:
                self._invoke_pending = False
                if self._invoke_callback:
                    self._invoke_callback()

        # if (lives <= 0 && Input.GetKeyDown(KeyCode.Return)) NewGame()
        if self.lives <= 0 and Input.get_key_down("return"):
            self._new_game()

    def _new_game(self):
        """private void NewGame()"""
        # gameOverUI.SetActive(false)
        if self.game_over_ui:
            self.game_over_ui.active = False
        if hasattr(self, '_status_text'):
            self._status_text.text = ""

        self._set_score(0)
        self._set_lives(3)
        self._new_round()

    def _new_round(self):
        """private void NewRound()"""
        # invaders.ResetInvaders(); invaders.gameObject.SetActive(true)
        if self.invaders:
            self.invaders.reset_invaders()
            self.invaders.game_object.active = True

        # for (int i = 0; i < bunkers.Length; i++) bunkers[i].ResetBunker()
        for i in range(len(self.bunkers)):
            self.bunkers[i].reset_bunker()

        self._respawn()

    def _respawn(self):
        """private void Respawn()"""
        # Vector3 position = player.transform.position; position.x = 0f
        if self.player:
            self.player.transform.position = Vector2(0, self.player.transform.position.y)
            self.player.game_object.active = True

    def _game_over(self):
        """private void GameOver()"""
        # gameOverUI.SetActive(true)
        if hasattr(self, '_status_text'):
            self._status_text.text = "GAME OVER — Press Enter"
        # invaders.gameObject.SetActive(false)
        if self.invaders:
            self.invaders.game_object.active = False

    def _set_score(self, score: int):
        """private void SetScore(int score)"""
        self.score = score
        # scoreText.text = score.ToString().PadLeft(4, '0')
        if self.score_text:
            self.score_text.text = str(score).zfill(4)
        self._update_title()

    def _set_lives(self, lives: int):
        """private void SetLives(int lives)"""
        # this.lives = Mathf.Max(lives, 0)
        self.lives = max(lives, 0)
        # livesText.text = this.lives.ToString()
        if self.lives_text:
            self.lives_text.text = str(self.lives)
        self._update_title()

    def on_player_killed(self, player=None):
        """public void OnPlayerKilled(Player player)"""
        self._set_lives(self.lives - 1)

        # player.gameObject.SetActive(false)
        if self.player:
            self.player.game_object.active = False

        # if (lives > 0) Invoke(nameof(NewRound), 1f)
        if self.lives > 0:
            self._invoke_callback = self._new_round
            self._invoke_delay = 1.0
            self._invoke_timer = 0.0
            self._invoke_pending = True
        else:
            self._game_over()

    def on_invader_killed(self, invader):
        """public void OnInvaderKilled(Invader invader)"""
        # invader.gameObject.SetActive(false)
        invader.game_object.active = False

        # SetScore(score + invader.score)
        self._set_score(self.score + invader.score)

        # if (invaders.GetAliveCount() == 0) NewRound()
        if self.invaders and self.invaders.get_alive_count() == 0:
            self._new_round()

    def on_mystery_ship_killed(self, mystery_ship):
        """public void OnMysteryShipKilled(MysteryShip mysteryShip)"""
        self._set_score(self.score + mystery_ship.score)

    def on_boundary_reached(self):
        """public void OnBoundaryReached()"""
        # if (invaders.gameObject.activeSelf)
        if self.invaders and self.invaders.game_object.active:
            self.invaders.game_object.active = False
            self.on_player_killed(self.player)

    def _setup_ui(self):
        """Create UI — maps to [SerializeField] references in C#."""
        from src.engine.lifecycle import LifecycleManager
        lm = LifecycleManager.instance()

        canvas_go = GameObject("UICanvas")
        canvas = canvas_go.add_component(Canvas)
        lm.register_component(canvas)

        # scoreText
        score_go = GameObject("ScoreText")
        rt = score_go.add_component(RectTransform)
        rt.anchor_min = Vector2(0, 1)
        rt.anchor_max = Vector2(0, 1)
        rt.anchored_position = Vector2(80, -15)
        rt.size_delta = Vector2(200, 30)
        self.score_text = score_go.add_component(Text)
        self.score_text.text = "0000"
        self.score_text.font_size = 20
        self.score_text.color = (255, 255, 255)
        self.score_text.alignment = TextAnchor.UPPER_LEFT

        # livesText
        lives_go = GameObject("LivesText")
        rt2 = lives_go.add_component(RectTransform)
        rt2.anchor_min = Vector2(1, 1)
        rt2.anchor_max = Vector2(1, 1)
        rt2.anchored_position = Vector2(-80, -15)
        rt2.size_delta = Vector2(200, 30)
        self.lives_text = lives_go.add_component(Text)
        self.lives_text.text = "3"
        self.lives_text.font_size = 20
        self.lives_text.color = (255, 255, 255)
        self.lives_text.alignment = TextAnchor.UPPER_RIGHT

        # gameOverUI (status text)
        status_go = GameObject("GameOverUI")
        self.game_over_ui = status_go
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
        GameManager.instance = None


# Need Time import for Invoke timer in update
from src.engine.time_manager import Time
