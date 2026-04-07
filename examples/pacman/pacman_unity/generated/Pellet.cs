using UnityEngine;
public class Pellet : MonoBehaviour
{
    public int points = 10;
    public static int PACMAN_LAYER = 7;
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
