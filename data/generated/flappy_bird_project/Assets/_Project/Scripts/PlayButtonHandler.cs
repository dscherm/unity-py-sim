using UnityEngine;

public class PlayButtonHandler : MonoBehaviour
{
    void Update()
    {
        if (Input.GetMouseButtonDown(0) || Input.GetKeyDown(KeyCode.Space))
        {
            if (GameManager.Instance != null
                && GameManager.Instance.playButton != null
                && GameManager.Instance.playButton.activeSelf)
            {
                GameManager.Instance.Play();
            }
        }
    }
}
