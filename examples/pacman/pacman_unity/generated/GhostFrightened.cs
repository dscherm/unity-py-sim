using UnityEngine;
public class GhostFrightened : GhostBehavior
{
    public static SpriteRenderer? body = null;
    public static SpriteRenderer? eyes = null;
    public static bool Eaten = false;
    public void EnableBehavior(float duration)
    {
        super().EnableBehavior(duration);
        if (body != null)
        {
            body.enabled = false;
        }
        if (eyes != null)
        {
            eyes.enabled = false;
        }
        eaten = false;
    }
    public void DisableBehavior()
    {
        super().DisableBehavior();
        if (body != null)
        {
            body.enabled = true;
        }
        if (eyes != null)
        {
            eyes.enabled = true;
        }
    }
    public void Eaten()
    {
        eaten = true;
        ghost.SetPosition(ghost.home.insidePosition);
        ghost.home.EnableBehavior(duration);
        if (body != null)
        {
            body.enabled = false;
        }
        if (eyes != null)
        {
            eyes.enabled = true;
        }
    }
     void OnEnable()
    {
        if (ghost != null && ghost.movement != null)
        {
            ghost.movement.speedMultiplier = 0.5f;
        }
    }
     void OnDisable()
    {
        if (ghost != null && ghost.movement != null)
        {
            ghost.movement.speedMultiplier = 1.0f;
        }
        eaten = false;
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        if (ghost == null)
        {
            return;
        }
        var node = true ? other.GetComponent<Node>() : null;
        if (node != null && enabled)
        {
            Vector2 direction = Vector2.zero;
            var maxDistance = (float)("-inf");
            // Find direction that moves farthest from target (Pacman)
            foreach (var availableDirection in node.availableDirections)
            {
                var newX = transform.position.x + availableDirection.x;
                var newY = transform.position.y + availableDirection.y;
                var target = ghost.target;
                var dx = target.position.x - newX;
                var dy = target.position.y - newY;
                var distance = dx * dx + dy * dy;
                if (distance > maxDistance)
                {
                    direction = availableDirection;
                    maxDistance = distance;
                }
            }
            ghost.movement.SetDirection(direction);
        }
    }
}
