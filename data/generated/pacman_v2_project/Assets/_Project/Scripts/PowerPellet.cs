using UnityEngine;
public class PowerPellet : Pellet
{
    public int points = 50;
    public float duration = 8.0f;
    public void Eat()
    {
        if (GameManager.instance != null)
        {
            GameManager.instance.PowerPelletEaten(this);
        }
    }
}
