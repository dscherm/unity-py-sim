using UnityEngine;
public class GhostScatter : GhostBehavior
{
     void OnDisable()
    {
        if (ghost != null && ghost.chase != null)
        {
            ghost.chase.Enable();
        }
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        var otherGo = getattr(other.gameObject, "gameObject", other.gameObject);
        var node = otherGo.GetComponent<Node>();
        if (node == null || !enabled)
        {
            return;
        }
        if (ghost != null && ghost.frightened != null && ghost.frightened.enabled)
        {
            return;
        }
        var movement = ghost != null ? ghost.movement : null;
        if (movement == null)
        {
            return;
        }
        var available = node.availableDirections;
        if (available == null)
        {
            return;
        }
        var direction = available[Random.Range(0, available.Count)];
        Vector2 reverse = new Vector2(-movement.direction.x, -movement.direction.y);
        if (direction.x == reverse.x && direction.y == reverse.y && available.Count > 1)
        {
            var idx = available.Index(direction);
            direction = available[(idx + 1) % available.Count];
        }
        movement.SetDirection(direction);
    }
}
