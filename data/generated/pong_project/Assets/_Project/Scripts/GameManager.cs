using UnityEngine;
namespace Pong
{
    [RequireComponent(typeof(BallController))]
    public class GameManager : MonoBehaviour
    {
        public float resetDelay = 1.0f;
        public bool isResetting = false;
        public float resetTimer = 0.0f;
        [SerializeField] private BallController ball;
         void Start()
        {
            GameObject ballObj = GameObject.Find("Ball");
            ball = ballObj.GetComponent<BallController>();
            ScoreManager.ResetScores();
        }
         void Update()
        {
            if (isResetting)
            {
                resetTimer -= Time.deltaTime;
                if (resetTimer <= 0)
                {
                    isResetting = false;
                    ball.Launch();
                }
            }
        }
        public void OnGoalScored(string side)
        {
            if (side == "left")
            {
                ScoreManager.AddScoreRight();
            }
            else
            {
                ScoreManager.AddScoreLeft();
            }
            ball.ResetState();
            isResetting = true;
            resetTimer = resetDelay;
        }
    }
}
