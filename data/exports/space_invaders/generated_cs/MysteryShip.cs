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
        left_destination = new Vector2(-8f, y);
        right_destination = new Vector2(8f, y);
        _despawn();
    }
     void Update()
    {
        if (_invoke_pending)
        {
            _invoke_timer += Time.deltaTime;
            if (_invoke_timer >= cycle_time)
            {
                _invoke_pending = false;
                _spawn();
            }
        }
        if (!spawned)
        {
            return;
        }
        if (direction == 1)
        {
            _move_right();
        }
        else
        {
            _move_left();
        }
    }
    public void MoveRight()
    {
        """private void MoveRight()""";
        var pos = transform.position;
        transform.position = new Vector2(;
        {
            pos.x + speed * Time.deltaTime,;
            pos.y,;
        }
        );
        if (transform.position.x >= right_destination.x)
        {
            _despawn();
        }
    }
    public void MoveLeft()
    {
        """private void MoveLeft()""";
        var pos = transform.position;
        transform.position = new Vector2(;
        {
            pos.x - speed * Time.deltaTime,;
            pos.y,;
        }
        );
        if (transform.position.x <= left_destination.x)
        {
            _despawn();
        }
    }
    public void Spawn()
    {
        """private void Spawn()""";
        direction *= -1;
        if (direction == 1)
        {
            transform.position = new Vector2(left_destination.x, left_destination.y);
        }
        else
        {
            transform.position = new Vector2(right_destination.x, right_destination.y);
        }
        spawned = true;
    }
    public void Despawn()
    {
        """private void Despawn()""";
        spawned = false;
        if (direction == 1)
        {
            transform.position = new Vector2(right_destination.x, right_destination.y);
        }
        else
        {
            transform.position = new Vector2(left_destination.x, left_destination.y);
        }
        _invoke_timer = 0f;
        _invoke_pending = true;
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        from space_invaders_python.player import LAYER_LASER;
        if (other.layer == LAYER_LASER)
        {
            _despawn();
            // GameManager.Instance.OnMysteryShipKilled(this)
            from space_invaders_python.game_manager import GameManager;
            if (GameManager.instance != null)
            {
                GameManager.instance.on_mystery_ship_killed(self);
            }
        }
    }
}
