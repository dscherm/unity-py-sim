using UnityEngine;
public class GhostHome : GhostBehavior
{
    private const int OBSTACLE_LAYER = 6;
    public GameObject? inside = null;
    public GameObject? outside = null;
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
        var otherGo = getattr(collision, "gameObject", collision);
        if (enabled && otherGo != null && otherGo.layer == OBSTACLE_LAYER)
        {
            if (ghost != null && ghost.movement != null)
            {
                var movement = ghost.movement;
                movement.SetDirection( new Vector2(-movement.direction.x, -movement.direction.y), true);
            }
        }
    }
    public IEnumerator ExitTransition()
    {
        var movement = ghost != null ? ghost.movement : null;
        if (movement == null)
        {
            return;
        }
        movement.SetDirection(new Vector2(0, 1), true);
        if (movement.rb != null)
        {
            movement.rb.isKinematic = true;
        }
        movement.enabled = false;
        var ghostGo = ghost.gameObject;
        Vector2 startPos = new Vector2(ghostGo.transform.position.x, ghostGo.transform.position.y);
        if (inside != null)
        {
            var target = inside.transform.position;
            var elapsed = 0.0f;
            while (elapsed < 0.5f)
            {
                var t = elapsed / 0.5f;
                var x = startPos.x + (target.x - startPos.x) * t;
                var y = startPos.y + (target.y - startPos.y) * t;
                ghostGo.transform.position = new Vector2(x, y);
                if (movement.rb != null)
                {
                    movement.rb.MovePosition(new Vector2(x, y));
                }
                elapsed += Time.deltaTime;
                yield return null;
            }
            ghostGo.transform.position = new Vector2(target.x, target.y);
            if (movement.rb != null)
            {
                movement.rb.MovePosition(new Vector2(target.x, target.y));
            }
        }
        if (outside != null)
        {
            Vector2 insidePos = new Vector2(ghostGo.transform.position.x, ghostGo.transform.position.y);
            target = outside.transform.position;
            elapsed = 0.0f;
            while (elapsed < 0.5f)
            {
                t = elapsed / 0.5f;
                x = insidePos.x + (target.x - insidePos.x) * t;
                y = insidePos.y + (target.y - insidePos.y) * t;
                ghostGo.transform.position = new Vector2(x, y);
                if (movement.rb != null)
                {
                    movement.rb.MovePosition(new Vector2(x, y));
                }
                elapsed += Time.deltaTime;
                yield return null;
            }
            ghostGo.transform.position = new Vector2(target.x, target.y);
            if (movement.rb != null)
            {
                movement.rb.MovePosition(new Vector2(target.x, target.y));
            }
        }
        var dirX = Random.value < 0.5f ? -1.0f : 1.0f;
        movement.SetDirection(new Vector2(dirX, 0), true);
        if (movement.rb != null)
        {
            movement.rb.isKinematic = false;
        }
        movement.enabled = true;
    }
}
