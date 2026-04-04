namespace Breakout
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
            remaining: list[GameObject] = GameObject.FindGameObjectsWithTag("Brick");
            active: list[GameObject] = [go for go in remaining if go.active];
            if (active.Count <= 0)
            {
                GameManager.gameWon = true;
                Debug.Log("You Win!");
            }
        }
        public void SetupUi()
        {
            canvas_go: GameObject = new GameObject("UICanvas");
            canvas: Canvas = canvas_go.AddComponent<Canvas>();
            score_go: GameObject = new GameObject("ScoreText");
            rt_score: RectTransform = score_go.AddComponent<RectTransform>();
            rt_score.anchorMin = new Vector2(0.0f, 1.0f);
            rt_score.anchorMax = new Vector2(0.0f, 1.0f);
            rt_score.anchoredPosition = new Vector2(100, -20);
            rt_score.sizeDelta = new Vector2(200, 30);
            scoreText: Text = score_go.AddComponent<Text>();
            scoreText.text = "Score: 0";
            scoreText.fontSize = 20;
            scoreText.color = new Color32(255, 255, 200, 255);
            scoreText.alignment = TextAnchor.UpperLeft;
            lives_go: GameObject = new GameObject("LivesText");
            rt_lives: RectTransform = lives_go.AddComponent<RectTransform>();
            rt_lives.anchorMin = new Vector2(1.0f, 1.0f);
            rt_lives.anchorMax = new Vector2(1.0f, 1.0f);
            rt_lives.anchoredPosition = new Vector2(-100, -20);
            rt_lives.sizeDelta = new Vector2(200, 30);
            livesText: Text = lives_go.AddComponent<Text>();
            livesText.text = "Lives: 3";
            livesText.fontSize = 20;
            livesText.color = new Color32(255, 200, 200, 255);
            livesText.alignment = TextAnchor.UpperRight;
            status_go: GameObject = new GameObject("StatusText");
            rt_status: RectTransform = status_go.AddComponent<RectTransform>();
            rt_status.anchorMin = new Vector2(0.5f, 1.0f);
            rt_status.anchorMax = new Vector2(0.5f, 1.0f);
            rt_status.anchoredPosition = new Vector2(0, -20);
            rt_status.sizeDelta = new Vector2(300, 30);
            statusText: Text = status_go.AddComponent<Text>();
            statusText.text = "Space to Launch";
            statusText.fontSize = 22;
            statusText.color = new Color32(255, 255, 255, 255);
            statusText.alignment = TextAnchor.UpperCenter;
        }
        public static void UpdateDisplay()
        {
            inst: GameManager | null = GameManager._instance;
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
