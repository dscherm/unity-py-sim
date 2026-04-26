using UnityEngine;
public class PowerPellet : Pellet
{
    [SerializeField] private GameManager gameManager;
    public int points = 50;
    public float duration = 8.0f;
    public void Eat()
    {
        if (gameManager != null)
        {
            gameManager.PowerPelletEaten(this);
        }
    }

    void Awake()
    {
        if (gameManager == null) gameManager = FindObjectOfType<GameManager>();
    }
}
