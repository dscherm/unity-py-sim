using UnityEngine;
public class Pellet : MonoBehaviour
{
    [SerializeField] private GameManager gameManager;
    public int points = 10;
    public static int PACMAN_LAYER = 3;
    public void Eat()
    {
        if (gameManager != null)
        {
            gameManager.PelletEaten(this);
        }
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        var otherGo = other.gameObject;
        if (otherGo.layer == PACMAN_LAYER)
        {
            Eat();
        }
    }

    void Awake()
    {
        if (gameManager == null) gameManager = FindObjectOfType<GameManager>();
    }
}
