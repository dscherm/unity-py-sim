using UnityEngine;
namespace PacmanV2
{
    public class GhostChase : GhostBehavior
    {
         void OnDisable()
        {
            if (ghost != null && ghost.scatter != null)
            {
                ghost.scatter.Enable();
            }
        }
         void OnTriggerEnter2D(Collider2D other)
        {
            var otherGo = other.gameObject;
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
            var target = ghost != null ? ghost.target : null;
            if (movement == null || target == null)
            {
                return;
            }
            var available = node.availableDirections;
            if (available == null)
            {
                return;
            }
            var targetPos = target.transform.position;
            var bestDir = available[0];
            var minDist = float.PositiveInfinity;
            foreach (var d in available)
            {
                // Don't reverse
                if (d.x == -movement.direction.x && d.y == -movement.direction.y)
                {
                    continue;
                }
                var pos = transform.position;
                var newX = pos.x + d.x;
                var newY = pos.y + d.y;
                var dx = targetPos.x - newX;
                var dy = targetPos.y - newY;
                var dist = dx * dx + dy * dy;
                if (dist < minDist)
                {
                    minDist = dist;
                    bestDir = d;
                }
            }
            movement.SetDirection(bestDir);
        }
    }
}
