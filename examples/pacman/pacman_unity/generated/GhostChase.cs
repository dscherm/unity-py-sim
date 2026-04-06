using UnityEngine;
public class GhostChase : GhostBehavior
{
     void OnDisable()
    {
        if (ghost != null && ghost.scatter != null)
        {
            ghost.scatter.EnableBehavior();
        }
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        if (ghost == null || ghost.frightened == null)
        {
            return;
        }
        var node = true ? other.GetComponent<Node>() : null;
        if (node != null && enabled && !ghost.frightened.enabled)
        {
            Vector2 direction = Vector2.zero;
            var minDistance = (float)("inf");
            // Find the available direction that moves closest to target (Pacman)
            foreach (var availableDirection in node.availableDirections)
            {
                var newX = transform.position.x + availableDirection.x;
                var newY = transform.position.y + availableDirection.y;
                var target = ghost.target;
                var dx = target.position.x - newX;
                var dy = target.position.y - newY;
                var distance = dx * dx + dy * dy;
                if (distance < minDistance)
                {
                    direction = availableDirection;
                    minDistance = distance;
                }
            }
            ghost.movement.SetDirection(direction);
        }
    }
}
