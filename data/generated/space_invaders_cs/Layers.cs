namespace SpaceInvaders
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
            position: Vector2 = transform.position;
            if (Keyboard.current.aKey.isPressed || Keyboard.current.leftArrowKey.isPressed)
            {
                Vector2 position = new Vector2(position.x - speed * Time.deltaTime, position.y);
            }
            else if (Keyboard.current.dKey.isPressed || Keyboard.current.rightArrowKey.isPressed)
            {
                position = new Vector2(position.x + speed * Time.deltaTime, position.y);
            }
            left_edge: float = -6.5f;
            right_edge: float = 6.5f;
            position = new Vector2( Mathf.Max(left_edge, Mathf.Min(right_edge, position.x)), position.y);
            transform.position = position;
            if ((Laser == null || !Laser.active) && (Keyboard.current.spaceKey.wasPressedThisFrame || Mouse.current.leftButton.wasPressedThisFrame))
            {
                // laser = Instantiate(laserPrefab, transform.position, Quaternion.identity)
                Laser = InstantiateLaser();
            }
        }
        public GameObject InstantiateLaser()
        {
            pos: Vector2 = new Vector2(transform.position.x, transform.position.y + 0.5f);
            laser: GameObject = Instantiate("Laser", position=pos);
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
