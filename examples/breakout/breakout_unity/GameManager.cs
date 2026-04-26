using UnityEngine;

public class GameManager : MonoBehaviour
{
    public static int Score { get; private set; }
    public static int Lives { get; set; } = 3;
    public static bool GameOver { get; private set; }
    public static bool GameWon { get; private set; }

    public static void Reset()
    {
        Score = 0;
        Lives = 3;
        GameOver = false;
        GameWon = false;
    }

    public static void AddScore(int points)
    {
        Score += points;
    }

    public static void OnBallLost()
    {
        if (GameOver || GameWon) return;
        Lives--;
        if (Lives <= 0)
        {
            GameOver = true;
            Debug.Log("Game Over!");
        }
    }

    public static void OnBrickDestroyed()
    {
        int remaining = GameObject.FindGameObjectsWithTag("Brick").Length;
        if (remaining <= 0)
        {
            GameWon = true;
            Debug.Log("You Win!");
        }
    }
}
