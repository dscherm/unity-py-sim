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
            GameManager.instance = this;
        }
    }
     void OnDestroy()
    {
        if (GameManager.instance is this)
        {
            GameManager.instance = null;
        }
    }
     void Start()
    {
        GameObject player_go = GameObject.Find("Player");
        if (player_go)
        {
            player = player_go.getComponent(Player);
        }
        GameObject invaders_go = GameObject.Find("InvadersGrid");
        if (invaders_go)
        {
            invaders = invaders_go.getComponent(Invaders);
        }
        GameObject ship_go = GameObject.Find("MysteryShip");
        if (ship_go)
        {
            mysteryShip = ship_go.getComponent(MysteryShip);
        }
        foreach (var go in GameObject.FindGameObjectsWithTag("Bunker"))
        {
            var bunker = go.getComponent(Bunker);
            if (bunker)
            {
                bunkers.Add(bunker);
            }
        }
        SetupUi();
        NewGame();
    }
     void Update()
    {
        if (_invokePending)
        {
            _invokeTimer += Time.deltaTime;
            if (_invokeTimer >= _invokeDelay)
            {
                _invokePending = false;
                if (_invokeCallback)
                {
                    InvokeCallback();
                }
            }
        }
        if (lives <= 0 && Input.GetKeyDown("return"))
        {
            NewGame();
        }
    }
    public void NewGame()
    {
        if (gameOverUI)
        {
            gameOverUI.active = false;
        }
        if (hasattr(this, "_statusText"))
        {
            _statusText.text = "";
        }
        SetScore(0);
        SetLives(3);
        NewRound();
    }
    public void NewRound()
    {
        if (invaders)
        {
            invaders.resetInvaders();
            invaders.gameObject.active = true;
        }
        for (int i = 0; i < bunkers.Count; i++)
        {
            bunkers[i].resetBunker();
        }
        Respawn();
    }
    public void Respawn()
    {
        if (player)
        {
            player.transform.position = new Vector2(0, player.transform.position.y);
            player.gameObject.active = true;
        }
    }
    public void GameOver()
    {
        if (hasattr(this, "_statusText"))
        {
            _statusText.text = "GAME OVER — Press Enter";
        }
        if (invaders)
        {
            invaders.gameObject.active = false;
        }
    }
    public void SetScore(int score)
    {
        score = score;
        if (scoreText)
        {
            scoreText.text = str(score).zfill(4);
        }
        UpdateTitle();
    }
    public void SetLives(int lives)
    {
        lives = max(lives, 0);
        if (livesText)
        {
            livesText.text = str(lives);
        }
        UpdateTitle();
    }
    public void OnPlayerKilled(object player)
    {
        SetLives(lives - 1);
        if (player)
        {
            player.gameObject.active = false;
        }
        if (lives > 0)
        {
            _invokeCallback = _new_round;
            _invokeDelay = 1f;
            _invokeTimer = 0f;
            _invokePending = true;
        }
        else
        {
            GameOver();
        }
    }
    public void OnInvaderKilled(object invader)
    {
        invader.gameObject.active = false;
        SetScore(score + invader.score);
        if (invaders && invaders.getAliveCount() == 0)
        {
            NewRound();
        }
    }
    public void OnMysteryShipKilled(object mysteryShip)
    {
        SetScore(score + mysteryShip.score);
    }
    public void OnBoundaryReached()
    {
        if (invaders && invaders.gameObject.active)
        {
            invaders.gameObject.active = false;
            onPlayerKilled(player);
        }
    }
    public void SetupUi()
    {
        var lm = LifecycleManager.instance();
        var canvas_go = new GameObject("UICanvas");
        var canvas = canvas_go.addComponent(Canvas);
        lm.registerComponent(canvas);
        var score_go = new GameObject("ScoreText");
        var rt = score_go.addComponent(RectTransform);
        rt.anchor_min = new Vector2(0, 1);
        rt.anchor_max = new Vector2(0, 1);
        rt.anchored_position = new Vector2(80, -15);
        rt.size_delta = new Vector2(200, 30);
        scoreText = score_go.addComponent(Text);
        scoreText.text = "0000";
        scoreText.font_size = 20;
        scoreText.color = (255, 255, 255);
        scoreText.alignment = TextAnchor.UPPER_LEFT;
        var lives_go = new GameObject("LivesText");
        var rt2 = lives_go.addComponent(RectTransform);
        rt2.anchor_min = new Vector2(1, 1);
        rt2.anchor_max = new Vector2(1, 1);
        rt2.anchored_position = new Vector2(-80, -15);
        rt2.size_delta = new Vector2(200, 30);
        livesText = lives_go.addComponent(Text);
        livesText.text = "3";
        livesText.font_size = 20;
        livesText.color = (255, 255, 255);
        livesText.alignment = TextAnchor.UPPER_RIGHT;
        var status_go = new GameObject("GameOverUI");
        gameOverUI = status_go;
        var rt3 = status_go.addComponent(RectTransform);
        rt3.anchor_min = new Vector2(0.5, 0.5);
        rt3.anchor_max = new Vector2(0.5, 0.5);
        rt3.anchored_position = Vector2.zero;
        rt3.size_delta = new Vector2(400, 40);
        _statusText = status_go.addComponent(Text);
        _statusText.text = "";
        _statusText.font_size = 28;
        _statusText.color = (255, 255, 100);
        _statusText.alignment = TextAnchor.MIDDLE_CENTER;
    }
    public void UpdateTitle()
    {
        try:;
        {
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
