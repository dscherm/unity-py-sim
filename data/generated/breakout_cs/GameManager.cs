using System.Linq;
using System;
using UnityEngine.UI;
using UnityEngine;
namespace Breakout
{
    public class GameManager : MonoBehaviour
    {
        public Canvas Canvas;
        public Text ScoreText;
        public Text LivesText;
        public Text StatusText;
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
            Canvas = canvasGo.AddComponent<Canvas>();
            GameObject scoreGo = new GameObject("ScoreText");
            RectTransform rtScore = scoreGo.AddComponent<RectTransform>();
            rtScore.anchorMin = new Vector2(0.0f, 1.0f);
            rtScore.anchorMax = new Vector2(0.0f, 1.0f);
            rtScore.anchoredPosition = new Vector2(100, -20);
            rtScore.sizeDelta = new Vector2(200, 30);
            ScoreText = scoreGo.AddComponent<Text>();
            ScoreText.text = "Score: 0";
            ScoreText.fontSize = 20;
            ScoreText.color = new Color32(255, 255, 200, 255);
            ScoreText.alignment = TextAnchor.UpperLeft;
            GameObject livesGo = new GameObject("LivesText");
            RectTransform rtLives = livesGo.AddComponent<RectTransform>();
            rtLives.anchorMin = new Vector2(1.0f, 1.0f);
            rtLives.anchorMax = new Vector2(1.0f, 1.0f);
            rtLives.anchoredPosition = new Vector2(-100, -20);
            rtLives.sizeDelta = new Vector2(200, 30);
            LivesText = livesGo.AddComponent<Text>();
            LivesText.text = "Lives: 3";
            LivesText.fontSize = 20;
            LivesText.color = new Color32(255, 200, 200, 255);
            LivesText.alignment = TextAnchor.UpperRight;
            GameObject statusGo = new GameObject("StatusText");
            RectTransform rtStatus = statusGo.AddComponent<RectTransform>();
            rtStatus.anchorMin = new Vector2(0.5f, 1.0f);
            rtStatus.anchorMax = new Vector2(0.5f, 1.0f);
            rtStatus.anchoredPosition = new Vector2(0, -20);
            rtStatus.sizeDelta = new Vector2(300, 30);
            StatusText = statusGo.AddComponent<Text>();
            StatusText.text = "Space to Launch";
            StatusText.fontSize = 22;
            StatusText.color = new Color32(255, 255, 255, 255);
            StatusText.alignment = TextAnchor.UpperCenter;
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
                dm._title = ( $"Breakout — Score: {GameManager.score}  |  Lives: {GameManager.lives}" );
            }
            catch (Exception) { }
        }
    }
}
