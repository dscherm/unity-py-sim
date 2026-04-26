using UnityEngine;
using FlappyBird;

// Hand-authored stub — was inline in examples/flappy_bird/run_flappy_bird.py
// and is intentionally filtered out by the translator (gap 4 / FU-1). It
// exists in the Unity tree so the pause→play transition has a trigger on
// the work machine where no UI Button click wiring gets round-tripped.
//
// FU-3 flipped GameManager.playButton to [SerializeField] private — this
// stub no longer peeks at it. It just fires Play() on any click/space while
// the game is paused (Time.timeScale == 0), which is the only state where
// clicking a play button is semantically meaningful anyway.
public class PlayButtonHandler : MonoBehaviour
{
    void Update()
    {
        if (Time.timeScale != 0f) return;

        if (Input.GetMouseButtonDown(0) || Input.GetKeyDown(KeyCode.Space))
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.Play();
            }
        }
    }
}
