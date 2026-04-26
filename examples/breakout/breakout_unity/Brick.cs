using UnityEngine;

public class Brick : MonoBehaviour
{
    [SerializeField] private int points = 10;
    [SerializeField] private int health = 1;

    void OnCollisionEnter2D(Collision2D collision)
    {
        if (collision.gameObject.CompareTag("Ball"))
        {
            health--;
            if (health <= 0)
            {
                DestroyBrick();
            }
        }
    }

    private void DestroyBrick()
    {
        GameManager.AddScore(points);
        Powerup.MaybeSpawn(transform.position);
        GameManager.OnBrickDestroyed();
        Destroy(gameObject);
    }
}
