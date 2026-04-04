namespace breakout
{
    using UnityEngine;
    using System;
    using System.Linq;
    using UnityEngine.UI;
    public class GameManager : MonoBehaviour
    {
        public static int score = 0;
        public static int lives = 3;
        public static bool gameOver = false;
        public static bool gameWon = false;
        public static GameManager Instance = null;
         void Start()
        {
            GameManager._instance = this;
            SetupUi();
        }
        public static GameManager? GetInstance()
        {
            return GameManager._instance;
        }
        public static void Reset()
        {
            GameManager.score = 0;
            GameManager.lives = 3;
            GameManager.gameOver = false;
            GameManager.gameWon = false;
            GameManager._instance = null;
        }
        public static void AddScore(int points)
        {
            GameManager.score += points;
            GameManager.UpdateDisplay();
        }
        public static void OnBallLost()
        {
            if (GameManager.gameOver || GameManager.gameWon)
            {
                return;
            }
            GameManager.lives -= 1;
            if (GameManager.lives <= 0)
            {
                GameManager.gameOver = true;
                Debug.Log("Game Over!");
            }
            GameManager.UpdateDisplay();
        }
        public static void OnBrickDestroyed()
        {
            GameObject[] remaining = GameObject.FindGameObjectsWithTag("Brick");
            GameObject[] active = remaining.Where(go => go.active).ToList();
            if (active.Count <= 0)
            {
                GameManager.gameWon = true;
                Debug.Log("You Win!");
            }
        }
        public void SetupUi()
        {
            GameObject canvasGo = new GameObject("UICanvas");
            canvas = canvasGo.AddComponent<Canvas>();
            GameObject scoreGo = new GameObject("ScoreText");
            RectTransform rtScore = scoreGo.AddComponent<RectTransform>();
            rtScore.anchorMin = new Vector2(0.0f, 1.0f);
            rtScore.anchorMax = new Vector2(0.0f, 1.0f);
            rtScore.anchoredPosition = new Vector2(100, -20);
            rtScore.sizeDelta = new Vector2(200, 30);
            scoreText = scoreGo.AddComponent<Text>();
            scoreText.text = "Score: 0";
            scoreText.fontSize = 20;
            scoreText.color = new Color32(255, 255, 200, 255);
            scoreText.alignment = TextAnchor.UpperLeft;
            GameObject livesGo = new GameObject("LivesText");
            RectTransform rtLives = livesGo.AddComponent<RectTransform>();
            rtLives.anchorMin = new Vector2(1.0f, 1.0f);
            rtLives.anchorMax = new Vector2(1.0f, 1.0f);
            rtLives.anchoredPosition = new Vector2(-100, -20);
            rtLives.sizeDelta = new Vector2(200, 30);
            livesText = livesGo.AddComponent<Text>();
            livesText.text = "Lives: 3";
            livesText.fontSize = 20;
            livesText.color = new Color32(255, 200, 200, 255);
            livesText.alignment = TextAnchor.UpperRight;
            GameObject statusGo = new GameObject("StatusText");
            RectTransform rtStatus = statusGo.AddComponent<RectTransform>();
            rtStatus.anchorMin = new Vector2(0.5f, 1.0f);
            rtStatus.anchorMax = new Vector2(0.5f, 1.0f);
            rtStatus.anchoredPosition = new Vector2(0, -20);
            rtStatus.sizeDelta = new Vector2(300, 30);
            statusText = statusGo.AddComponent<Text>();
            statusText.text = "Space to Launch";
            statusText.fontSize = 22;
            statusText.color = new Color32(255, 255, 255, 255);
            statusText.alignment = TextAnchor.UpperCenter;
        }
        public static void UpdateDisplay()
        {
            GameManager inst = GameManager._instance;
            if (inst != null && true)
            {
                inst._score_text.text = $"Score: {GameManager.score}";
                inst._lives_text.text = $"Lives: {GameManager.lives}";
                if (GameManager.gameOver)
                {
                    inst._status_text.text = "Game Over!";
                }
                else if (GameManager.gameWon)
                {
                    inst._status_text.text = "You Win!";
                }
                else
                {
                    inst._status_text.text = "";
                }
            }
            try
            {
            }
            catch (Exception) { }
        }
    }
}
