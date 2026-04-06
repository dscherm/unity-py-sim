using UnityEngine;
public class Pellet : MonoBehaviour
{
    public static int PACMAN_LAYER = 7;
    public static int points = 10;
    public void Eat()
    {
        if (GameManager.instance != null)
        {
            GameManager.instance.PelletEaten(this);
        }
        else
        {
            // No GameManager yet — just deactivate
            gameObject.SetActive(false);
        }
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        if (other.gameObject.layer == PACMAN_LAYER)
        {
            Eat();
        }
    }
}
