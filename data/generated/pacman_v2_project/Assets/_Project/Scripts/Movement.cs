using UnityEngine;
[RequireComponent(typeof(Rigidbody2D))]
public class Movement : MonoBehaviour
{
    public float speed = 8.0f;
    public float speedMultiplier = 1.0f;
    public Vector2 initialDirection = new Vector2(0, 0);
    public int obstacleLayer = OBSTACLE_LAYER;
    public Vector2 direction = new Vector2(0, 0);
    public Vector2 nextDirection = new Vector2(0, 0);
    public Vector2 startingPosition = new Vector2(0, 0);
    public Rigidbody2D rb;
    public static int OBSTACLE_LAYER = 6;
    public static float CELL_SIZE = 1.0f;
    public static float GRID_OFFSET = 0.5f;
     void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
        startingPosition = new Vector2( transform.position.x, transform.position.y );
    }
     void Start()
    {
        ResetState();
    }
    public void ResetState()
    {
        speedMultiplier = 1.0f;
        direction = new Vector2(initialDirection.x, initialDirection.y);
        nextDirection = Vector2.zero;
        Vector2 newPos = new Vector2(startingPosition.x, startingPosition.y);
        transform.position = newPos;
        if (rb != null)
        {
            rb.MovePosition(newPos);
        }
        enabled = true;
    }
     void Update()
    {
        if (nextDirection.x != 0 || nextDirection.y != 0)
        {
            SetDirection(nextDirection);
        }
    }
     void FixedUpdate()
    {
        if (rb == null || (direction.x == 0 && direction.y == 0))
        {
            return;
        }
        if (Occupied(direction))
        {
            return;
        }
        var pos = transform.position;
        var step = speed * speedMultiplier * Time.fixedDeltaTime;
        Vector2 newPos = new Vector2( pos.x + direction.x * step, pos.y + direction.y * step);
        rb.MovePosition(newPos);
        transform.position = newPos;
    }
    public void SetDirection(Vector2 direction, bool forced = false)
    {
        Vector2 snapped = default;
        if (forced)
        {
            this.direction = direction;
            nextDirection = Vector2.zero;
            return;
        }
        var pos = transform.position;
        var changingAxis = ( (direction.x != 0 && this.direction.y != 0) || (direction.y != 0 && this.direction.x != 0) );
        if (changingAxis)
        {
            if (direction.x != 0)
            {
                snapped = new Vector2(pos.x, Mathf.Round(pos.y / CELL_SIZE) * CELL_SIZE);
            }
            else
            {
                snapped = new Vector2( Mathf.Round((pos.x - GRID_OFFSET) / CELL_SIZE) * CELL_SIZE + GRID_OFFSET, pos.y);
            }
            Vector2 checkPos = new Vector2( snapped.x + direction.x * 1.0f, snapped.y + direction.y * 1.0f);
            var hit = Physics2D.OverlapBox(checkPos, new Vector2(0.4f, 0.4f), 0.0f, 1 << obstacleLayer);
            if (hit == null)
            {
                transform.position = snapped;
                rb.MovePosition(snapped);
                this.direction = direction;
                nextDirection = Vector2.zero;
            }
            else
            {
                nextDirection = direction;
            }
        }
        else
        {
            if (!Occupied(direction))
            {
                this.direction = direction;
                nextDirection = Vector2.zero;
            }
            else
            {
                nextDirection = direction;
            }
        }
    }
    public bool Occupied(Vector2 direction)
    {
        var pos = transform.position;
        Vector2 checkPos = new Vector2( pos.x + direction.x * 0.5f, pos.y + direction.y * 0.5f);
        var hit = Physics2D.OverlapBox(checkPos, new Vector2(0.25f, 0.25f), 0.0f, 1 << obstacleLayer);
        return hit != null;
    }
}
