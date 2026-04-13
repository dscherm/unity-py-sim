using System.Linq;
using UnityEngine.UI;
using UnityEngine;
public class GameManager : MonoBehaviour
{
    [SerializeField] private Canvas Canvas;
    [SerializeField] private Text ScoreText;
    [SerializeField] private Text LivesText;
    [SerializeField] private Text StatusText;
    public static int score = 0;
    public static int lives = 3;
    public static bool gameOver = false;
    public static bool gameWon = false;
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
        GameObject canvasGo = new GameObject("UICanvas"); // TODO: wire via Inspector or Instantiate
        Canvas = canvasGo.AddComponent<Canvas>();
        GameObject scoreGo = new GameObject("ScoreText"); // TODO: wire via Inspector or Instantiate
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
        GameObject livesGo = new GameObject("LivesText"); // TODO: wire via Inspector or Instantiate
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
        GameObject statusGo = new GameObject("StatusText"); // TODO: wire via Inspector or Instantiate
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
