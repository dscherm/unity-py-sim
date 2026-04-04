using UnityEngine.InputSystem;
using UnityEngine;
namespace SpaceInvaders
{
    public class Layers
    {
        public static int LASER = 8;
        public static int MISSILE = 9;
        public static int INVADER = 10;
        public static int BOUNDARY = 11;
    }
    public class Player : MonoBehaviour
    {
        public float speed = 5f;
        public GameObject laserPrefab;
        public GameObject Laser;
         void Update()
        {
            Vector2 position = transform.position;
            if (Keyboard.current.aKey.isPressed || Keyboard.current.leftArrowKey.isPressed)
            {
                position = new Vector2(position.x - speed * Time.deltaTime, position.y);
            }
            else if (Keyboard.current.dKey.isPressed || Keyboard.current.rightArrowKey.isPressed)
            {
                position = new Vector2(position.x + speed * Time.deltaTime, position.y);
            }
            float leftEdge = -6.5f;
            float rightEdge = 6.5f;
            position = new Vector2( Mathf.Max(leftEdge, Mathf.Min(rightEdge, position.x)), position.y);
            transform.position = position;
            if ((Laser == null || !Laser.active) && (Keyboard.current.spaceKey.wasPressedThisFrame || Mouse.current.leftButton.wasPressedThisFrame))
            {
                // laser = Instantiate(laserPrefab, transform.position, Quaternion.identity)
                Laser = InstantiateLaser();
            }
        }
        public GameObject InstantiateLaser()
        {
            Vector2 pos = new Vector2(transform.position.x, transform.position.y + 0.5f);
            GameObject laser = Instantiate(laserPrefab, pos, Quaternion.identity);
            laser.layer = Layers.Laser;
            return laser;
        }
         void OnTriggerEnter2D(Collider2D other)
        {
            if (other.gameObject.layer == Layers.Missile || other.gameObject.layer == Layers.Invader)
            {
                // GameManager.Instance.OnPlayerKilled(this)
                if (GameManager.instance != null)
                {
                    GameManager.instance.OnPlayerKilled(this);
                }
            }
        }
    }
}
