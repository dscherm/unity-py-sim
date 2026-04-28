using UnityEngine;
namespace SpaceInvaders
{
    public class MysteryShip : MonoBehaviour
    {
    [SerializeField] private GameManager gameManager;
        public float speed = 5.0f;
        public float cycleTime = 30.0f;
        public int score = 300;
        public Vector2 leftDestination = new Vector2(-8, 0);
        public Vector2 rightDestination = new Vector2(8, 0);
        public int direction = -1;
        public bool spawned = false;
        public float invokeTimer = 0.0f;
        public bool invokePending = false;
         void Start()
        {
            float y = transform.position.y;
            leftDestination = new Vector2(-8.0f, y);
            rightDestination = new Vector2(8.0f, y);
            Despawn();
        }
         void Update()
        {
            if (invokePending)
            {
                invokeTimer += Time.deltaTime;
                if (invokeTimer >= cycleTime)
                {
                    invokePending = false;
                    Spawn();
                }
            }
            if (!spawned)
            {
                return;
            }
            if (direction == 1)
            {
                MoveRight();
            }
            else
            {
                MoveLeft();
            }
        }
        public void MoveRight()
        {
            Vector2 pos = transform.position;
            transform.position = new Vector2( pos.x + speed * Time.deltaTime, pos.y);
            if (transform.position.x >= rightDestination.x)
            {
                Despawn();
            }
        }
        public void MoveLeft()
        {
            Vector2 pos = transform.position;
            transform.position = new Vector2( pos.x - speed * Time.deltaTime, pos.y);
            if (transform.position.x <= leftDestination.x)
            {
                Despawn();
            }
        }
        public void Spawn()
        {
            direction *= -1;
            if (direction == 1)
            {
                transform.position = new Vector2(leftDestination.x, leftDestination.y);
            }
            else
            {
                transform.position = new Vector2(rightDestination.x, rightDestination.y);
            }
            spawned = true;
        }
        public void Despawn()
        {
            spawned = false;
            if (direction == 1)
            {
                transform.position = new Vector2(rightDestination.x, rightDestination.y);
            }
            else
            {
                transform.position = new Vector2(leftDestination.x, leftDestination.y);
            }
            invokeTimer = 0.0f;
            invokePending = true;
        }
         void OnTriggerEnter2D(Collider2D other)
        {
            if (other.gameObject.layer == Layers.LASER)
            {
                Despawn();
                // gameManager.OnMysteryShipKilled(this)
                if (gameManager != null)
                {
                    gameManager.OnMysteryShipKilled(this);
                }
            }
        }

    void Awake()
    {
        if (gameManager == null) gameManager = FindObjectOfType<GameManager>();
    }
}
}
