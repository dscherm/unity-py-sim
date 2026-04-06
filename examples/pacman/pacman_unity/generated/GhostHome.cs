using UnityEngine;
public class GhostHome : GhostBehavior
{
    private const int OBSTACLE_LAYER = 6;
    public static Vector2 insidePosition = new Vector2(0, 0);
    public static Vector2 outsidePosition = new Vector2(0, 0);
     void OnEnable()
    {
        pass;
    }
     void OnDisable()
    {
        if (gameObject.activeSelf)
        {
            StartCoroutine(ExitTransition());
        }
    }
     void OnCollisionEnter2D(Collision2D collision)
    {
        if (ghost == null)
        {
            return;
        }
        var go = getattr(collision, "gameObject", collision);
        if (go != null && enabled && go.layer == OBSTACLE_LAYER)
        {
            ghost.movement.SetDirection( new Vector2( -ghost.movement.direction.x, -ghost.movement.direction.y), true);
        }
    }
    public IEnumerator ExitTransition()
    {
        ghost.movement.SetDirection(new Vector2(0, 1), true);
        ghost.movement.enabled = false;
        Vector2 pos = new Vector2(transform.position.x, transform.position.y);
        var duration = 0.5f;
        var elapsed = 0.0f;
        while (elapsed < duration)
        {
            var t = elapsed / duration;
            var x = pos.x + (inside_position.x - pos.x) * t;
            var y = pos.y + (inside_position.y - pos.y) * t;
            ghost.SetPosition(new Vector2(x, y));
            elapsed += Time.deltaTime;
            yield return null;
        }
        elapsed = 0.0f;
        while (elapsed < duration)
        {
            t = elapsed / duration;
            x = inside_position.x + (outside_position.x - inside_position.x) * t;
            y = inside_position.y + (outside_position.y - inside_position.y) * t;
            ghost.SetPosition(new Vector2(x, y));
            elapsed += Time.deltaTime;
            yield return null;
        }
        var dirX = Random.value < 0.5f ? -1.0f : 1.0f;
        ghost.movement.SetDirection(new Vector2(dirX, 0), true);
        ghost.movement.enabled = true;
    }
}
