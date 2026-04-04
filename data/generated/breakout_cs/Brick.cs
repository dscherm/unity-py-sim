using System;
using UnityEngine;
namespace Breakout
{
    public class Brick : MonoBehaviour
    {
        public int points = 10;
        public int health = 1;
         void OnCollisionEnter2D(Collision2D collision)
        {
            if (collision.gameObject.tag == "Ball" || collision.gameObject.name == "Ball")
            {
                health -= 1;
                if (health <= 0)
                {
                    Destroy();
                }
            }
        }
        public void Destroy()
        {
            GameManager.AddScore(points);
            maybe_spawn_powerup(transform.position);
            gameObject.SetActive(false);
            BoxCollider2D collider = GetComponent<BoxCollider2D>();
            GameManager.OnBrickDestroyed();
        }
    }
}
