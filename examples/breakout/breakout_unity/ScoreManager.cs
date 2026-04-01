using UnityEngine;
using TMPro;

public class ScoreManager : MonoBehaviour
{
    [SerializeField] private TextMeshProUGUI scoreText;
    [SerializeField] private TextMeshProUGUI livesText;

    void Update()
    {
        if (scoreText != null)
            scoreText.text = $"Score: {GameManager.Score}";
        if (livesText != null)
            livesText.text = $"Lives: {GameManager.Lives}";
    }
}
