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
    [SerializeField] private GameManager gameManager;
        public float speed = 5.0f;
        [SerializeField] private GameObject laserPrefab;
        [SerializeField] private GameObject laser;
        public static object LAYER_LASER = Layers.LASER;
        public static object LAYER_MISSILE = Layers.MISSILE;
        public static object LAYER_INVADER = Layers.INVADER;
        public static object LAYER_BOUNDARY = Layers.BOUNDARY;
         void Update()
        {
            Vector2 position = transform.position;
            if (Keyboard.current?.aKey.isPressed == true || Keyboard.current?.leftArrowKey.isPressed == true)
            {
                position = new Vector2(position.x - speed * Time.deltaTime, position.y);
            }
            else if (Keyboard.current?.dKey.isPressed == true || Keyboard.current?.rightArrowKey.isPressed == true)
            {
                position = new Vector2(position.x + speed * Time.deltaTime, position.y);
            }
            float leftEdge = -6.5f;
            float rightEdge = 6.5f;
            position = new Vector2( Mathf.Max(leftEdge, Mathf.Min(rightEdge, position.x)), position.y);
            transform.position = position;
            if ((laser == null || !laser.activeSelf) && (Keyboard.current?.spaceKey.wasPressedThisFrame == true || Mouse.current?.leftButton.wasPressedThisFrame == true))
            {
                // laser = Instantiate(laserPrefab, transform.position, Quaternion.identity)
                laser = InstantiateLaser();
            }
        }
        public GameObject InstantiateLaser()
        {
            Vector2 pos = new Vector2(transform.position.x, transform.position.y + 0.5f);
            GameObject laser = Instantiate(laserPrefab, pos, Quaternion.identity);
            laser.layer = Layers.LASER;
            return laser;
        }
         void OnTriggerEnter2D(Collider2D other)
        {
            if (other.gameObject.layer == Layers.MISSILE || other.gameObject.layer == Layers.INVADER)
            {
                // gameManager.OnPlayerKilled(this)
                if (gameManager != null)
                {
                    gameManager.OnPlayerKilled(this);
                }
            }
        }

    void Awake()
    {
        if (gameManager == null) gameManager = FindObjectOfType<GameManager>();
    }
}
}
