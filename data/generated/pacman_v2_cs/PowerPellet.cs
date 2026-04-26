using UnityEngine;
public class PowerPellet : Pellet
{
    public int points = 50;
    public float duration = 8.0f;
    public void Eat()
    {
        if (GameManager.Instance != null)
        {
            GameManager.Instance.PowerPelletEaten(this);
        }
    }
}
