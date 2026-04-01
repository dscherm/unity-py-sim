using UnityEngine;

// Unity APIs used: MonoBehaviour, static fields
public class ScoreManager : MonoBehaviour
{
    public static int ScoreLeft { get; private set; }
    public static int ScoreRight { get; private set; }
    public static int WinScore = 5;

    public static void AddScoreLeft()
    {
        ScoreLeft++;
        CheckWin();
    }

    public static void AddScoreRight()
    {
        ScoreRight++;
        CheckWin();
    }

    public static void ResetScores()
    {
        ScoreLeft = 0;
        ScoreRight = 0;
    }

    private static void CheckWin()
    {
        if (ScoreLeft >= WinScore)
        {
            Debug.Log("Left Player Wins!");
        }
        else if (ScoreRight >= WinScore)
        {
            Debug.Log("Right Player Wins!");
        }
    }
}
