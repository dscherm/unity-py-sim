using System.Collections.Generic;
using System;
using UnityEngine;
public class GameManager : MonoBehaviour
{
    public int score = 0;
    public int lives = 3;
    public int GhostMultiplier = 1;
    public GameManager? instance;
    public object? pacman;
    public List<object> ghosts;
    public List<object> AllPellets;
    public object ghosts;
    public object AllPellets;
     void Awake()
    {
        if (GameManager.instance != null)
        {
            gameObject.SetActive(false);
            return;
        }
        GameManager.instance = this;
    }
     void OnDestroy()
    {
        if (GameManager.instance == this)
        {
            GameManager.instance = null;
        }
    }
     void Start()
    {
        AllPellets = ( GameObject.FindGameObjectsWithTag("Pellet") + GameObject.FindGameObjectsWithTag("PowerPellet") );
        NewGame();
    }
     void Update()
    {
        if (lives <= 0 && Input.GetKeyDown(KeyCode.Return))
        {
            NewGame();
        }
    }
    public void NewGame()
    {
        SetScore(0);
        SetLives(3);
        NewRound();
    }
    public void NewRound()
    {
        foreach (var go in AllPellets)
        {
            go.SetActive(true);
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
    public void SetLives(int lives)
    {
        lives = lives;
        UpdateTitle();
    }
    public void SetScore(int score)
    {
        score = score;
        UpdateTitle();
    }
    public void PacmanEaten()
    {
        if (pacman != null)
        {
            pacman.DeathSequenceStart();
        }
        SetLives(lives - 1);
        if (lives > 0)
        {
            invoke("ResetState", 3.0f);
        }
        else
        {
            GameOver();
        }
    }
    public void GhostEaten(object ghost)
    {
        var points = ghost.points * GhostMultiplier;
        SetScore(score + points);
        GhostMultiplier *= 2;
        ghost.frightened.Eaten();
    }
    public void PelletEaten(Component pellet)
    {
        pellet.gameObject.SetActive(false);
        SetScore(score + pellet.points);
        if (!HasRemainingPellets())
        {
            if (pacman != null)
            {
                pacman.gameObject.SetActive(false);
            }
            invoke("NewRound", 3.0f);
        }
    }
    public void PowerPelletEaten(object pellet)
    {
        foreach (var ghost in ghosts)
        {
            ghost.frightened.Enable(pellet.duration);
        }
        PelletEaten(pellet);
        CancelInvoke("ResetGhostMultiplier");
        invoke("ResetGhostMultiplier", pellet.duration);
    }
    public bool HasRemainingPellets()
    {
        foreach (var go in AllPellets)
        {
            if (go.activeSelf)
            {
                return true;
            }
        }
        return false;
    }
    public void ResetGhostMultiplier()
    {
        GhostMultiplier = 1;
    }
    public void UpdateTitle()
    {
        try
        {
            pygame.display.SetCaption( $"Pacman — Score: {score}  Lives: {lives}" );
        }
    }
}
