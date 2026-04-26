using UnityEngine;
public class PowerPellet : Pellet
{
    public float duration = 8.0f;
    public void Eat()
    {
        if (GameManager.instance != null)
        {
            GameManager.instance.PowerPelletEaten(this);
        }
        else
        {
            // No GameManager yet — just deactivate
            gameObject.SetActive(false);
        }
    }
}
