using UnityEngine;
public class GhostHome : GhostBehavior
{
    private const int OBSTACLE_LAYER = 6;
    public Transform? inside = null;
    public Transform? outside = null;
     void OnEnable()
    {
        StopAllCoroutines();
    }
     void OnDisable()
    {
        if (ghost != null && gameObject.activeSelf)
        {
            StartCoroutine(ExitTransition());
        }
    }
     void OnCollisionEnter2D(Collision2D collision)
    {
        var go = getattr(collision, "gameObject", collision);
        if (enabled && go != null && go.layer == OBSTACLE_LAYER)
        {
            ghost.movement.SetDirection( new Vector2( -ghost.movement.direction.x, -ghost.movement.direction.y), true);
        }
    }
    public IEnumerator ExitTransition()
    {
        ghost.movement.SetDirection(new Vector2(0, 1), true);
        ghost.movement.rb.isKinematic = true;
        ghost.movement.enabled = false;
        Vector2 position = new Vector2(transform.position.x, transform.position.y);
        var duration = 0.5f;
        var elapsed = 0.0f;
        while (elapsed < duration)
        {
            var t = elapsed / duration;
            var x = position.x + (inside.position.x - position.x) * t;
            var y = position.y + (inside.position.y - position.y) * t;
            ghost.SetPosition(new Vector2(x, y));
            elapsed += Time.deltaTime;
            yield return null;
        }
        elapsed = 0.0f;
        while (elapsed < duration)
        {
            t = elapsed / duration;
            x = inside.position.x + (outside.position.x - inside.position.x) * t;
            y = inside.position.y + (outside.position.y - inside.position.y) * t;
            ghost.SetPosition(new Vector2(x, y));
            elapsed += Time.deltaTime;
            yield return null;
        }
        var dirX = Random.value < 0.5f ? -1.0f : 1.0f;
        ghost.movement.SetDirection(new Vector2(dirX, 0), true);
        ghost.movement.rb.isKinematic = false;
        ghost.movement.enabled = true;
    }
}
