using UnityEngine;
[RequireComponent(typeof(Rigidbody2D))]
public class Movement : MonoBehaviour
{
    public bool enabled;
    public static int OBSTACLE_LAYER = 6;
    public static float speed = 8.0f;
    public static float speedMultiplier = 1.0f;
    public static Vector2 initialDirection = new Vector2(0, 0);
    public static int obstacleLayer = OBSTACLE_LAYER;
    public static Rigidbody2D rb = null;
    public static Vector2 direction = new Vector2(0, 0);
    public static Vector2 nextDirection = new Vector2(0, 0);
    public static Vector2 startingPosition = new Vector2(0, 0);
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
        transform.position = new Vector2( startingPosition.x, startingPosition.y );
        if (rb != null)
        {
            rb.bodyType = RigidbodyType2D.Kinematic;
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
        if (rb == null)
        {
            return;
        }
        if (direction.x == 0 && direction.y == 0)
        {
            return;
        }
        if (Occupied(direction))
        {
            return;
        }
        var pos = transform.position;
        Vector2 translation = new Vector2( speed * speedMultiplier * Time.fixedDeltaTime * direction.x, speed * speedMultiplier * Time.fixedDeltaTime * direction.y);
        Vector2 newPos = new Vector2(pos.x + translation.x, pos.y + translation.y);
        rb.MovePosition(newPos);
        transform.position = newPos;
    }
    public void SetDirection(Vector2 direction, bool forced)
    {
        if (forced != null || !Occupied(direction))
        {
            direction = direction;
            nextDirection = Vector2.zero;
        }
        else
        {
            nextDirection = direction;
        }
    }
    public bool Occupied(Vector2 direction)
    {
        Unity's BoxCast sweeps && finds exact contact. We approximate by;
        checking overlap at exactly 1 grid cell (1.0f unit) ahead with a;
        small box. This lets Pacman move right up to the wall edge.;
        var pos = transform.position;
        var checkDist = 0.55f;
        Vector2 checkPos = new Vector2( pos.x + direction.x * checkDist, pos.y + direction.y * checkDist);
        var hit = Physics2D.OverlapBox( point=checkPos, new Vector2(0.3f, 0.3f), 0.0f, 1 << obstacleLayer);
        return hit != null;
    }
}
