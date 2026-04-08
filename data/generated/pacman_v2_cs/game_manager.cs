using System.Collections.Generic;
using System;
using UnityEngine;
public class GameManager : MonoBehaviour
{
    public int score = 0;
    public int lives = 3;
    public int ghostMultiplier = 1;
    public float DeferredTimer = 0.0f;
    public List<Ghost> ghosts = new List<Ghost>();
    public List<Pellet> AllPellets = new List<Pellet>();
    public GameManager? instance;
    public List<Ghost> ghosts;
    public Pacman pacman;
    public List<Pellet> AllPellets;
    public string DeferredAction;
     void Awake()
    {
        GameManager.instance = this;
    }
     void Update()
    {
        if (DeferredAction != null)
        {
            DeferredTimer -= Time.deltaTime;
            if (DeferredTimer <= 0)
            {
                var action = DeferredAction;
                DeferredAction = null;
                getattr(this, action)();
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
        foreach (var pellet in AllPellets)
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
            DeferredAction = "NewRound";
            DeferredTimer = 3.0f;
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
            DeferredAction = "ResetState";
            DeferredTimer = 3.0f;
        }
        else
        {
            DeferredAction = "GameOver";
            DeferredTimer = 3.0f;
        }
    }
    public bool HasRemainingPellets()
    {
        foreach (var pellet in AllPellets)
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
        try
        {
            pygame.display.SetCaption($"Pacman V2 — Score: {score}  Lives: {lives}");
            /* pass */
        }
    }
    public void RegisterPellet(Pellet pellet)
    {
        if (!AllPellets.Contains(pellet))
        {
            AllPellets.Add(pellet);
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
