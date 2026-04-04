namespace spaceinvaders
{
    using UnityEngine;
    using System;
    using System.Collections.Generic;
    using UnityEngine.InputSystem;
    using UnityEngine.UI;
    [RequireComponent(typeof(Bunker))]
    [RequireComponent(typeof(Invaders))]
    [RequireComponent(typeof(MysteryShip))]
    [RequireComponent(typeof(Player))]
    public class GameManager : MonoBehaviour
    {
        public List<Bunker> bunkers = new List<Bunker>();
        public int score = 0;
        public int lives = 3;
        public float InvokeTimer = 0f;
        public bool InvokePending = false;
        public GameObject gameOverUi;
        public Text scoreText;
        public Text livesText;
        public Player player;
        public Invaders invaders;
        public MysteryShip mysteryShip;
        public System.Action invokeCallback;
        public static GameManager instance = null;
         void Awake()
        {
            if (GameManager.instance != null)
            {
                gameObject.SetActive(false);
            }
            else
            {
                GameManager.instance = this;
            }
        }
         void OnDestroy()
        {
            if (GameManager.instance == this)
            {
                GameManager.instance = null;
            }
        }
         void Start()
        {
            GameObject playerGo = GameObject.Find("Player");
            if (playerGo != null)
            {
                player = playerGo.GetComponent<Player>();
            }
            GameObject invadersGo = GameObject.Find("InvadersGrid");
            if (invadersGo != null)
            {
                invaders = invadersGo.GetComponent<Invaders>();
            }
            GameObject shipGo = GameObject.Find("MysteryShip");
            if (shipGo != null)
            {
                mysteryShip = shipGo.GetComponent<MysteryShip>();
            }
            foreach (var go in GameObject.FindGameObjectsWithTag("Bunker"))
            {
                Bunker bunker = go.GetComponent<Bunker>();
                if (bunker != null)
                {
                    bunkers.Add(bunker);
                }
            }
            SetupUi();
            NewGame();
        }
         void Update()
        {
            if (InvokePending != null)
            {
                InvokeTimer += Time.deltaTime;
                if (InvokeTimer >= invokeDelay)
                {
                    InvokePending = false;
                    if (invokeCallback != null)
                    {
                        invokeCallback?.Invoke();
                    }
                }
            }
            if (lives <= 0 && Keyboard.current.enterKey.wasPressedThisFrame)
            {
                NewGame();
            }
        }
        public void NewGame()
        {
            if (gameOverUi != null)
            {
                gameOverUi.SetActive(false);
            }
            if (true)
            {
                statusText.text = "";
            }
            SetScore(0);
            SetLives(3);
            NewRound();
        }
        public void NewRound()
        {
            if (invaders != null)
            {
                invaders.ResetInvaders();
                invaders.gameObject.SetActive(true);
            }
            for (int i = 0; i < bunkers.Count; i++)
            {
                bunkers[i].ResetBunker();
            }
            Respawn();
        }
        public void Respawn()
        {
            if (player != null)
            {
                player.transform.position = new Vector2(0, player.transform.position.y);
                player.gameObject.SetActive(true);
            }
        }
        public void GameOver()
        {
            if (true)
            {
                statusText.text = "GAME OVER — Press Enter";
            }
            if (invaders != null)
            {
                invaders.gameObject.SetActive(false);
            }
        }
        public void SetScore(int score)
        {
            score = score;
            if (scoreText != null)
            {
                scoreText.text = score.ToString().PadLeft(4, "0"[0]);
            }
            UpdateTitle();
        }
        public void SetLives(int lives)
        {
            lives = Mathf.Max(lives, 0);
            if (livesText != null)
            {
                livesText.text = lives.ToString();
            }
            UpdateTitle();
        }
        public void OnPlayerKilled(Player? player)
        {
            SetLives(lives - 1);
            if (player != null)
            {
                player.gameObject.SetActive(false);
            }
            if (lives > 0)
            {
                invokeCallback = NewRound;
                invokeDelay = 1.0f;
                InvokeTimer = 0.0f;
                InvokePending = true;
            }
            else
            {
                GameOver();
            }
        }
        public void OnInvaderKilled(Invader invader)
        {
            invader.gameObject.SetActive(false);
            SetScore(score + invader.score);
            if (invaders != null && invaders.GetAliveCount() == 0)
            {
                NewRound();
            }
        }
        public void OnMysteryShipKilled(MysteryShip mysteryShip)
        {
            SetScore(score + mysteryShip.score);
        }
        public void OnBoundaryReached()
        {
            if (invaders != null && invaders.gameObject.activeSelf)
            {
                invaders.gameObject.SetActive(false);
                OnPlayerKilled(player);
            }
        }
        public void SetupUi()
        {
            GameObject canvasGo = new GameObject("UICanvas");
            Canvas canvas = canvasGo.AddComponent<Canvas>();
            GameObject scoreGo = new GameObject("ScoreText");
            RectTransform rt = scoreGo.AddComponent<RectTransform>();
            rt.anchorMin = new Vector2(0, 1);
            rt.anchorMax = new Vector2(0, 1);
            rt.anchoredPosition = new Vector2(80, -15);
            rt.sizeDelta = new Vector2(200, 30);
            scoreText = scoreGo.AddComponent<Text>();
            scoreText.text = "0000";
            scoreText.fontSize = 20;
            scoreText.color = new Color32(255, 255, 255, 255);
            scoreText.alignment = TextAnchor.UpperLeft;
            GameObject livesGo = new GameObject("LivesText");
            RectTransform rt2 = livesGo.AddComponent<RectTransform>();
            rt2.anchorMin = new Vector2(1, 1);
            rt2.anchorMax = new Vector2(1, 1);
            rt2.anchoredPosition = new Vector2(-80, -15);
            rt2.sizeDelta = new Vector2(200, 30);
            livesText = livesGo.AddComponent<Text>();
            livesText.text = "3";
            livesText.fontSize = 20;
            livesText.color = new Color32(255, 255, 255, 255);
            livesText.alignment = TextAnchor.UpperRight;
            GameObject statusGo = new GameObject("GameOverUI");
            gameOverUi = statusGo;
            RectTransform rt3 = statusGo.AddComponent<RectTransform>();
            rt3.anchorMin = new Vector2(0.5f, 0.5f);
            rt3.anchorMax = new Vector2(0.5f, 0.5f);
            rt3.anchoredPosition = Vector2.zero;
            rt3.sizeDelta = new Vector2(400, 40);
            statusText = statusGo.AddComponent<Text>();
            statusText.text = "";
            statusText.fontSize = 28;
            statusText.color = new Color32(255, 255, 100, 255);
            statusText.alignment = TextAnchor.MiddleCenter;
        }
        public void UpdateTitle()
        {
            try
            {
            }
            catch (Exception) { }
        }
        public static void Reset()
        {
            GameManager.instance = null;
        }
    }
}
