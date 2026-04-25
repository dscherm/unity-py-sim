using System.Collections.Generic;
using System.Linq;
using UnityEngine.UI;
using UnityEngine;
namespace Breakout
{
    public class GameManager : MonoBehaviour
    {
        [SerializeField] private Canvas canvas;
        [SerializeField] private Text scoreText;
        [SerializeField] private Text livesText;
        [SerializeField] private Text statusText;
        public static int score = 0;
        public static int lives = 3;
        public static bool gameOver = false;
        public static bool gameWon = false;
    // Singleton — wire via Inspector [SerializeField] on dependents
        public static GameManager Instance = null;
         void Start()
        {
            GameManager.Instance = this;
            SetupUi();
        }
        public static GameManager GetInstance()
        {
            return GameManager.Instance;
        }
        public static void ResetState()
        {
            GameManager.score = 0;
            GameManager.lives = 3;
            GameManager.gameOver = false;
            GameManager.gameWon = false;
            GameManager.Instance = null;
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
            GameObject[] active = remaining.Where(go => go.activeSelf).ToArray();
            if (active.Length <= 0)
            {
                GameManager.gameWon = true;
                Debug.Log("You Win!");
            }
        }
        public void SetupUi()
        {
            GameObject canvasGo = (GameObject.Find("UICanvas") ?? new GameObject("UICanvas")); // TODO: wire via Inspector or Instantiate
            canvas = canvasGo.AddComponent<Canvas>();
            GameObject scoreGo = (GameObject.Find("ScoreText") ?? new GameObject("ScoreText")); // TODO: wire via Inspector or Instantiate
            RectTransform rtScore = scoreGo.AddComponent<RectTransform>();
            rtScore.anchorMin = new Vector2(0.0f, 1.0f);
            rtScore.anchorMax = new Vector2(0.0f, 1.0f);
            rtScore.anchoredPosition = new Vector2(100, -20);
            rtScore.sizeDelta = new Vector2(200, 30);
            scoreText = scoreGo.AddComponent<Text>();
            if (scoreText != null && scoreText.font == null) scoreText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            scoreText.text = "Score: 0";
            scoreText.fontSize = 20;
            scoreText.color = new Color32(255, 255, 200, 255);
            scoreText.alignment = TextAnchor.UpperLeft;
            GameObject livesGo = (GameObject.Find("LivesText") ?? new GameObject("LivesText")); // TODO: wire via Inspector or Instantiate
            RectTransform rtLives = livesGo.AddComponent<RectTransform>();
            rtLives.anchorMin = new Vector2(1.0f, 1.0f);
            rtLives.anchorMax = new Vector2(1.0f, 1.0f);
            rtLives.anchoredPosition = new Vector2(-100, -20);
            rtLives.sizeDelta = new Vector2(200, 30);
            livesText = livesGo.AddComponent<Text>();
            if (livesText != null && livesText.font == null) livesText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            livesText.text = "Lives: 3";
            livesText.fontSize = 20;
            livesText.color = new Color32(255, 200, 200, 255);
            livesText.alignment = TextAnchor.UpperRight;
            GameObject statusGo = (GameObject.Find("StatusText") ?? new GameObject("StatusText")); // TODO: wire via Inspector or Instantiate
            RectTransform rtStatus = statusGo.AddComponent<RectTransform>();
            rtStatus.anchorMin = new Vector2(0.5f, 1.0f);
            rtStatus.anchorMax = new Vector2(0.5f, 1.0f);
            rtStatus.anchoredPosition = new Vector2(0, -20);
            rtStatus.sizeDelta = new Vector2(300, 30);
            statusText = statusGo.AddComponent<Text>();
            if (statusText != null && statusText.font == null) statusText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            statusText.text = "Space to Launch";
            statusText.fontSize = 22;
            statusText.color = new Color32(255, 255, 255, 255);
            statusText.alignment = TextAnchor.UpperCenter;
        }
        public static void UpdateDisplay()
        {
            GameManager inst = GameManager.Instance;
            if (inst != null)
            {
                inst.ScoreText.text = $"Score: {GameManager.score}";
                inst.LivesText.text = $"Lives: {GameManager.lives}";
                if (GameManager.gameOver)
                {
                    inst.StatusText.text = "Game Over!";
                }
                else if (GameManager.gameWon)
                {
                    inst.StatusText.text = "You Win!";
                }
                else
                {
                    inst.StatusText.text = "";
                }
                /* pass */
            }
        }
    }
}
