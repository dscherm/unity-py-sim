using System.Collections.Generic;
using System.Collections;
using System;
using UnityEngine;
public class GameManager : MonoBehaviour
{
    public object ghosts;
    public object AllPellets;
    public static 'GameManager | None' instance = null;
    public static int score = 0;
    public static int lives = 3;
    public static int GhostMultiplier = 1;
    public static object? pacman = null;
    public static List<object> ghosts = null;
    public static List<object> AllPellets = null;
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
        score = 0;
        lives = 3;
        NewRound();
    }
    public void NewRound()
    {
        foreach (var go in AllPellets)
        {
            go.SetActive(true);
        }
        ResetState();
        UpdateTitle();
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
        UpdateTitle();
    }
    public void PelletEaten(Component pellet)
    {
        pellet.gameObject.SetActive(false);
        score += pellet.points;
        UpdateTitle();
        if (!HasRemainingPellets())
        {
            if (pacman != null)
            {
                pacman.gameObject.SetActive(false);
            }
            StartCoroutine(NewRoundDelay(3.0f));
        }
    }
    public void PowerPelletEaten(object pellet)
    {
        foreach (var ghost in ghosts)
        {
            ghost.frightened.EnableBehavior(pellet.duration);
        }
        PelletEaten(pellet);
        GhostMultiplier = 1;
    }
    public void GhostEaten(object ghost)
    {
        var points = ghost.points * GhostMultiplier;
        score += points;
        GhostMultiplier *= 2;
        UpdateTitle();
    }
    public void PacmanEaten()
    {
        if (pacman != null)
        {
            pacman.DeathSequenceStart();
        }
        lives -= 1;
        UpdateTitle();
        if (lives > 0)
        {
            StartCoroutine(ResetStateDelay(3.0f));
        }
        else
        {
            GameOver();
        }
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
    public IEnumerator NewRoundDelay(float delay)
    {
        yield return new WaitForSeconds(delay);
        NewRound();
    }
    public IEnumerator ResetStateDelay(float delay)
    {
        yield return new WaitForSeconds(delay);
        ResetState();
    }
    public void UpdateTitle()
    {
        try
        {
            pygame.display.SetCaption( $"Pacman — Score: {score}  Lives: {lives}" );
        }
    }
}
