using UnityEngine;
public class Pellet : MonoBehaviour
{
    public int points = 10;
    public static int PACMAN_LAYER = 3;
    public void Eat()
    {
        if (GameManager.instance != null)
        {
            GameManager.instance.PelletEaten(this);
        }
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        var otherGo = getattr(other.gameObject, "gameObject", other.gameObject);
        if (otherGo.layer == PACMAN_LAYER)
        {
            Eat();
        }
    }
}
