using UnityEngine;
[RequireComponent(typeof(Bunker))]
[RequireComponent(typeof(Invaders))]
[RequireComponent(typeof(MysteryShip))]
[RequireComponent(typeof(Player))]
public class GameManager : MonoBehaviour
{
    [SerializeField] private list bunkers = [];
    [SerializeField] private int score = 0;
    [SerializeField] private int lives = 3;
    [SerializeField] private float InvokeTimer = 0f;
    [SerializeField] private bool InvokePending = false;
    private GameObject? gameOverUi;
    private Text? scoreText;
    private Text? livesText;
    private var player;
    private var invaders;
    private var mysteryShip;
    private var InvokeCallback;
    public static var instance = null;
     void Awake()
    {
        if (GameManager.instance != null)
        {
            game_object.active = false;
        }
        else
        {
            GameManager.instance = self;
        }
    }
     void OnDestroy()
    {
        if (GameManager.instance is self)
        {
            GameManager.instance = null;
        }
    }
     void Start()
    {
        from space_invaders_python.player import Player;
        from space_invaders_python.invaders import Invaders;
        from space_invaders_python.mystery_ship import MysteryShip;
        from space_invaders_python.bunker import Bunker;
        GameObject player_go = GameObject.Find("Player");
        if (player_go)
        {
            player = player_go.get_component(Player);
        }
        GameObject invaders_go = GameObject.Find("InvadersGrid");
        if (invaders_go)
        {
            invaders = invaders_go.get_component(Invaders);
        }
        GameObject ship_go = GameObject.Find("MysteryShip");
        if (ship_go)
        {
            mystery_ship = ship_go.get_component(MysteryShip);
        }
        foreach (var go in GameObject.FindGameObjectsWithTag("Bunker"))
        {
            var bunker = go.get_component(Bunker);
            if (bunker)
            {
                bunkers.Add(bunker);
            }
        }
        _setup_ui();
        _new_game();
    }
     void Update()
    {
        if (_invoke_pending)
        {
            _invoke_timer += Time.deltaTime;
            if (_invoke_timer >= _invoke_delay)
            {
                _invoke_pending = false;
                if (_invoke_callback)
                {
                    _invoke_callback();
                }
            }
        }
        if (lives <= 0 && Input.GetKeyDown("return"))
        {
            _new_game();
        }
    }
    public void NewGame()
    {
        """private void NewGame()""";
        if (game_over_ui)
        {
            game_over_ui.active = false;
        }
        if (hasattr(self, "_status_text"))
        {
            _status_text.text = "";
        }
        _set_score(0);
        _set_lives(3);
        _new_round();
    }
    public void NewRound()
    {
        """private void NewRound()""";
        if (invaders)
        {
            invaders.reset_invaders();
            invaders.gameObject.active = true;
        }
        for (int i = 0; i < bunkers.Count; i++)
        {
            bunkers[i].reset_bunker();
        }
        _respawn();
    }
    public void Respawn()
    {
        """private void Respawn()""";
        if (player)
        {
            player.transform.position = new Vector2(0, player.transform.position.y);
            player.gameObject.active = true;
        }
    }
    public void GameOver()
    {
        """private void GameOver()""";
        if (hasattr(self, "_status_text"))
        {
            _status_text.text = "GAME OVER — Press Enter";
        }
        if (invaders)
        {
            invaders.gameObject.active = false;
        }
    }
    public void SetScore(int score)
    {
        """private void SetScore(int score)""";
        score = score;
        if (score_text)
        {
            score_text.text = str(score).zfill(4);
        }
        _update_title();
    }
    public void SetLives(int lives)
    {
        """private void SetLives(int lives)""";
        lives = max(lives, 0);
        if (lives_text)
        {
            lives_text.text = str(lives);
        }
        _update_title();
    }
    public void OnPlayerKilled(object player)
    {
        """public void OnPlayerKilled(Player player)""";
        _set_lives(lives - 1);
        if (player)
        {
            player.gameObject.active = false;
        }
        if (lives > 0)
        {
            _invoke_callback = _new_round;
            _invoke_delay = 1f;
            _invoke_timer = 0f;
            _invoke_pending = true;
        }
        else
        {
            _game_over();
        }
    }
    public void OnInvaderKilled(object invader)
    {
        """public void OnInvaderKilled(Invader invader)""";
        invader.gameObject.active = false;
        _set_score(score + invader.score);
        if (invaders && invaders.get_alive_count() == 0)
        {
            _new_round();
        }
    }
    public void OnMysteryShipKilled(object mysteryShip)
    {
        """public void OnMysteryShipKilled(MysteryShip mysteryShip)""";
        _set_score(score + mystery_ship.score);
    }
    public void OnBoundaryReached()
    {
        """public void OnBoundaryReached()""";
        if (invaders && invaders.gameObject.active)
        {
            invaders.gameObject.active = false;
            on_player_killed(player);
        }
    }
    public void SetupUi()
    {
        """Create UI — maps to [SerializeField] references in C#.""";
        from src.engine.lifecycle import LifecycleManager;
        var lm = LifecycleManager.instance();
        var canvas_go = new GameObject("UICanvas");
        var canvas = canvas_go.add_component(Canvas);
        lm.register_component(canvas);
        var score_go = new GameObject("ScoreText");
        var rt = score_go.add_component(RectTransform);
        rt.anchor_min = new Vector2(0, 1);
        rt.anchor_max = new Vector2(0, 1);
        rt.anchored_position = new Vector2(80, -15);
        rt.size_delta = new Vector2(200, 30);
        score_text = score_go.add_component(Text);
        score_text.text = "0000";
        score_text.font_size = 20;
        score_text.color = (255, 255, 255);
        score_text.alignment = TextAnchor.UPPER_LEFT;
        var lives_go = new GameObject("LivesText");
        var rt2 = lives_go.add_component(RectTransform);
        rt2.anchor_min = new Vector2(1, 1);
        rt2.anchor_max = new Vector2(1, 1);
        rt2.anchored_position = new Vector2(-80, -15);
        rt2.size_delta = new Vector2(200, 30);
        lives_text = lives_go.add_component(Text);
        lives_text.text = "3";
        lives_text.font_size = 20;
        lives_text.color = (255, 255, 255);
        lives_text.alignment = TextAnchor.UPPER_RIGHT;
        var status_go = new GameObject("GameOverUI");
        game_over_ui = status_go;
        var rt3 = status_go.add_component(RectTransform);
        rt3.anchor_min = new Vector2(0.5, 0.5);
        rt3.anchor_max = new Vector2(0.5, 0.5);
        rt3.anchored_position = Vector2.zero;
        rt3.size_delta = new Vector2(400, 40);
        _status_text = status_go.add_component(Text);
        _status_text.text = "";
        _status_text.font_size = 28;
        _status_text.color = (255, 255, 100);
        _status_text.alignment = TextAnchor.MIDDLE_CENTER;
    }
    public void UpdateTitle()
    {
        try:;
        {
            from src.engine.rendering.display import DisplayManager;
            var dm = DisplayManager.instance();
            dm._title = f"Space Invaders — Score: {score} | Lives: {lives}";
        }
        except Exception:;
    }
    public static void Reset()
    {
        GameManager.instance = null;
    }
}
