using UnityEngine;
public class MysteryShip : MonoBehaviour
{
    [SerializeField] private float speed = 5f;
    [SerializeField] private float cycleTime = 30f;
    [SerializeField] private int score = 300;
    [SerializeField] private Vector2 leftDestination = Vector2(-8, 0);
    [SerializeField] private Vector2 rightDestination = Vector2(8, 0);
    [SerializeField] private int direction = -1;
    [SerializeField] private bool spawned = false;
    [SerializeField] private float InvokeTimer = 0f;
    [SerializeField] private bool InvokePending = false;
     void Start()
    {
        var y = transform.position.y;
        leftDestination = new Vector2(-8f, y);
        rightDestination = new Vector2(8f, y);
        Despawn();
    }
     void Update()
    {
        if (_invokePending)
        {
            _invokeTimer += Time.deltaTime;
            if (_invokeTimer >= cycleTime)
            {
                _invokePending = false;
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
        var pos = transform.position;
        transform.position = new Vector2(pos.x + speed * Time.deltaTime, pos.y);
        if (transform.position.x >= rightDestination.x)
        {
            Despawn();
        }
    }
    public void MoveLeft()
    {
        var pos = transform.position;
        transform.position = new Vector2(pos.x - speed * Time.deltaTime, pos.y);
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
        _invokeTimer = 0f;
        _invokePending = true;
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        if (other.layer == LAYER_LASER)
        {
            Despawn();
            // GameManager.Instance.OnMysteryShipKilled(this)
            if (GameManager.instance != null)
            {
                GameManager.instance.onMysteryShipKilled(this);
            }
        }
    }
}
