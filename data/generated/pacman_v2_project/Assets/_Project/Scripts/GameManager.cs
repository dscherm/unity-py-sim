using System.Collections.Generic;
using UnityEngine;
namespace PacmanV2
{
    public class GameManager : MonoBehaviour
    {
        public int score = 0;
        public int lives = 3;
        public int ghostMultiplier = 1;
        public float deferredTimer = 0.0f;
        [SerializeField] private List<Ghost> ghosts = new List<Ghost>();
        [SerializeField] private Pacman pacman;
        [SerializeField] private List<Pellet> allPellets = new List<Pellet>();
        public string deferredAction;
    // Singleton — wire via Inspector [SerializeField] on dependents
        public static GameManager Instance = null;
         void Awake()
        {
            GameManager.Instance = this;
        }
         void Update()
        {
            if (deferredAction != null)
            {
                deferredTimer -= Time.deltaTime;
                if (deferredTimer <= 0)
                {
                    var action = deferredAction;
                    deferredAction = null;
                    this.SendMessage(action);
                }
            }
        }
         void Start()
        {
            NewGame();
        }
        public void NewGame()
        {
            score = 0;
            lives = 3;
            NewRound();
        }
        public void NewRound()
        {
            foreach (var pellet in allPellets)
            {
                pellet.gameObject.SetActive(true);
            }
            ResetState();
        }
        public void ResetState()
        {
            foreach (var ghost in ghosts)
            {
                ghost.ResetState();
            }
            if (pacman != null)
            {
                pacman.ResetState();
            }
        }
        public void GameOver()
        {
            foreach (var ghost in ghosts)
            {
                ghost.gameObject.SetActive(false);
            }
            if (pacman != null)
            {
                pacman.gameObject.SetActive(false);
            }
        }
        public void PelletEaten(Pellet pellet)
        {
            pellet.gameObject.SetActive(false);
            SetScore(score + pellet.points);
            if (!HasRemainingPellets())
            {
                // Hide Pacman until new round starts (matches V1 behavior)
                if (pacman != null)
                {
                    pacman.gameObject.SetActive(false);
                }
                deferredAction = "NewRound";
                deferredTimer = 3.0f;
            }
        }
        public void PowerPelletEaten(PowerPellet pellet)
        {
            foreach (var ghost in ghosts)
            {
                if (ghost.frightened != null)
                {
                    ghost.frightened.Enable(pellet.duration);
                }
            }
            ghostMultiplier = 1;
            PelletEaten(pellet);
        }
        public void GhostEaten(Ghost ghost)
        {
            SetScore(score + ghost.points * ghostMultiplier);
            ghostMultiplier += 1;
            if (ghost.frightened != null)
            {
                ghost.frightened.Eat();
            }
        }
        public void PacmanEaten()
        {
            if (pacman != null)
            {
                pacman.DeathSequenceStart();
            }
            foreach (var ghost in ghosts)
            {
                ghost.gameObject.SetActive(false);
            }
            lives -= 1;
            if (lives > 0)
            {
                deferredAction = "ResetState";
                deferredTimer = 3.0f;
            }
            else
            {
                deferredAction = "GameOver";
                deferredTimer = 3.0f;
            }
        }
        public bool HasRemainingPellets()
        {
            foreach (var pellet in allPellets)
            {
                if (pellet.gameObject.activeSelf)
                {
                    return true;
                }
            }
            return false;
        }
        public void SetScore(int value)
        {
            score = value;
        }
        public void RegisterPellet(Pellet pellet)
        {
            if (!allPellets.Contains(pellet))
            {
                allPellets.Add(pellet);
            }
        }
        public void RegisterGhost(Ghost ghost)
        {
            if (!ghosts.Contains(ghost))
            {
                ghosts.Add(ghost);
            }
        }
    }
}
