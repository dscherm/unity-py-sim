using UnityEngine.UI;
using UnityEngine;
public class GameManager : MonoBehaviour
{
    public int score = 0;
    [SerializeField] private MonoBehaviour player;
    [SerializeField] private MonoBehaviour spawner;
    [SerializeField] private Text scoreText;
    [SerializeField] private GameObject playButton;
    [SerializeField] private GameObject gameOverDisplay;
    // Singleton — wire via Inspector [SerializeField] on dependents
    public static GameManager Instance = null;
     void Awake()
    {
        if (GameManager.Instance != null)
        {
            DestroyImmediate(gameObject);
        }
        else
        {
            GameManager.Instance = this;
        }
    }
     void OnDestroy()
    {
        if (GameManager.Instance == this)
        {
            GameManager.Instance = null;
        }
    }
     void Start()
    {
        Pause();
    }
    public void Pause()
    {
        Time.timeScale = 0.0f;
        if (player != null)
        {
            player.enabled = false;
        }
    }
    public void Play()
    {
        score = 0;
        if (scoreText != null)
        {
            scoreText.text = score.ToString();
        }
        if (playButton != null)
        {
            playButton.SetActive(false);
        }
        if (gameOverDisplay != null)
        {
            gameOverDisplay.SetActive(false);
        }
        Time.timeScale = 1.0f;
        if (player != null)
        {
            player.enabled = true;
        }
        var pipes = FindObjectsOfType<Pipes>();
        for (int i = 0; i < pipes.Length; i++)
        {
            Destroy(pipes[i].gameObject);
        }
    }
    public void GameOver()
    {
        if (playButton != null)
        {
            playButton.SetActive(true);
        }
        if (gameOverDisplay != null)
        {
            gameOverDisplay.SetActive(true);
        }
        Pause();
    }
    public void IncreaseScore()
    {
        score += 1;
        if (scoreText != null)
        {
            scoreText.text = score.ToString();
        }
    }
}
