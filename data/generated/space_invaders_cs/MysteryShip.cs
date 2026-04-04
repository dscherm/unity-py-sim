using UnityEngine;
namespace SpaceInvaders
{
    public class MysteryShip : MonoBehaviour
    {
        public float speed = 5f;
        public float cycleTime = 30f;
        public int score = 300;
        public Vector2 leftDestination = new Vector2(-8, 0);
        public Vector2 rightDestination = new Vector2(8, 0);
        public int direction = -1;
        public bool spawned = false;
        public float InvokeTimer = 0f;
        public bool InvokePending = false;
         void Start()
        {
            float y = transform.position.y;
            leftDestination = new Vector2(-8.0f, y);
            rightDestination = new Vector2(8.0f, y);
            Despawn();
        }
         void Update()
        {
            if (InvokePending)
            {
                InvokeTimer += Time.deltaTime;
                if (InvokeTimer >= cycleTime)
                {
                    InvokePending = false;
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
            InvokeTimer = 0.0f;
            InvokePending = true;
        }
         void OnTriggerEnter2D(Collider2D other)
        {
            if (other.gameObject.layer == Layers.Laser)
            {
                Despawn();
                // GameManager.Instance.OnMysteryShipKilled(this)
                if (GameManager.instance != null)
                {
                    GameManager.instance.OnMysteryShipKilled(this);
                }
            }
        }
    }
}
