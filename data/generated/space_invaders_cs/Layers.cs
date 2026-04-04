namespace spaceinvaders
{
    using UnityEngine;

    public class Layers
    {
        public static int LASER = 8;
        public static int MISSILE = 9;
        public static int INVADER = 10;
        public static int BOUNDARY = 11;
    }
    using UnityEngine;
    using UnityEngine.InputSystem;
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
            GameObject laser = Instantiate("Laser", position=pos);
            laser.layer = Layers.LASER;
            return laser;
        }
         void OnTriggerEnter2D(GameObject other)
        {
            if (other.gameObject.layer == Layers.MISSILE || other.gameObject.layer == Layers.INVADER)
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
