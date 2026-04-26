using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine.UI;

namespace AngryBirds
{
    public class GameManager : MonoBehaviour
    {
        public static GameState CurrentGameState = GameState.Start;

        [SerializeField] private SlingShot slingshot;
        [SerializeField] private Text statusText;
        [SerializeField] private Text scoreText;
        [SerializeField] private Text birdsText;

        private int currentBirdIndex;
        private List<GameObject> Birds;
        private List<GameObject> Pigs;
        private List<GameObject> Bricks;
        private int score;

        void Start()
        {
            CurrentGameState = GameState.Start;
            Birds = new List<GameObject>(GameObject.FindGameObjectsWithTag("Bird"));
            Pigs = new List<GameObject>(GameObject.FindGameObjectsWithTag("Pig"));
            Bricks = new List<GameObject>(GameObject.FindGameObjectsWithTag("Brick"));
        }

        void Update()
        {
            switch (CurrentGameState)
            {
                case GameState.Start:
                    if (Input.GetMouseButtonUp(0))
                    {
                        LoadNextBird();
                        CurrentGameState = GameState.Playing;
                    }
                    break;
                case GameState.Playing:
                    if (slingshot.slingshotState == SlingshotState.BirdFlying)
                    {
                        if (AllStopped() || Time.time - slingshot.TimeSinceThrown > Constants.SettleTimeout)
                        {
                            StartCoroutine(NextTurn());
                        }
                    }
                    break;
            }
            UpdateUI();
        }

        IEnumerator NextTurn()
        {
            yield return new WaitForSeconds(1.0f);

            if (AllPigsDestroyed())
            {
                score += 1000;
                CurrentGameState = GameState.Won;
                yield break;
            }

            currentBirdIndex++;
            if (currentBirdIndex >= Birds.Count)
            {
                CurrentGameState = GameState.Lost;
                yield break;
            }

            LoadNextBird();
            slingshot.slingshotState = SlingshotState.Idle;
        }

        private void LoadNextBird()
        {
            if (currentBirdIndex < Birds.Count && Birds[currentBirdIndex] != null)
            {
                slingshot.BirdToThrow = Birds[currentBirdIndex];
                Birds[currentBirdIndex].transform.position = slingshot.transform.position;
            }
        }

        private bool AllStopped()
        {
            foreach (var obj in Birds.Concat(Pigs).Concat(Bricks))
            {
                if (obj != null)
                {
                    var rb = obj.GetComponent<Rigidbody2D>();
                    if (rb != null && rb.linearVelocity.sqrMagnitude > Constants.MinVelocity)
                        return false;
                }
            }
            return true;
        }

        private bool AllPigsDestroyed()
        {
            return Pigs.All(p => p == null);
        }

        private void UpdateUI()
        {
            int pigsLeft = Pigs.Count(p => p != null);
            int birdsLeft = Birds.Count - currentBirdIndex;

            if (statusText != null)
            {
                switch (CurrentGameState)
                {
                    case GameState.Start: statusText.text = "Click to Start"; break;
                    case GameState.Playing: statusText.text = $"Pigs: {pigsLeft}"; break;
                    case GameState.Won: statusText.text = "You Win!"; break;
                    case GameState.Lost: statusText.text = "You Lost!"; break;
                }
            }
            if (scoreText != null) scoreText.text = $"Score: {score}";
            if (birdsText != null) birdsText.text = $"Birds: {birdsLeft}";
        }
    }
}
