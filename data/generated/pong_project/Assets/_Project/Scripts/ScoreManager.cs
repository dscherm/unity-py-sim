using UnityEngine;
namespace Pong
{
    public class ScoreManager : MonoBehaviour
    {
        public static int scoreLeft = 0;
        public static int scoreRight = 0;
        public static int winScore = 5;
        public static void AddScoreLeft()
        {
            ScoreManager.scoreLeft += 1;
            ScoreManager.CheckWin();
        }
        public static void AddScoreRight()
        {
            ScoreManager.scoreRight += 1;
            ScoreManager.CheckWin();
        }
        public static void ResetScores()
        {
            ScoreManager.scoreLeft = 0;
            ScoreManager.scoreRight = 0;
        }
        public static void CheckWin()
        {
            if (ScoreManager.scoreLeft >= ScoreManager.winScore)
            {
                Debug.Log("Left Player Wins!");
            }
            else if (ScoreManager.scoreRight >= ScoreManager.winScore)
            {
                Debug.Log("Right Player Wins!");
            }
        }
    }
}
