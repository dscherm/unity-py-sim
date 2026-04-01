using UnityEngine;

// Unity APIs used: MonoBehaviour, GameObject.Find, GetComponent, Transform, OnTriggerEnter2D
public class GameManager : MonoBehaviour
{
    [SerializeField] private float resetDelay = 1f;

    private BallController ball;
    private bool isResetting = false;
    private float resetTimer = 0f;

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

        ball.Reset();
        isResetting = true;
        resetTimer = resetDelay;
    }
}
