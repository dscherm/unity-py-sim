using UnityEngine;
public class GhostFrightened : GhostBehavior
{
    public SpriteRenderer? body = null;
    public SpriteRenderer? eyes = null;
    public bool Eaten = false;
    public Color32 OriginalColor = new Color32(255, 255, 255, 255);
    public void Enable(float duration)
    {
        super().Enable(duration);
        if (body != null)
        {
            originalColor = body.color;
            body.color = new Color32(33, 33, 222, 255);
        }
        eaten = false;
    }
    public void Disable()
    {
        super().Disable();
        if (body != null)
        {
            body.color = originalColor;
        }
    }
    public void Eaten()
    {
        eaten = true;
        ghost.SetPosition(ghost.home.inside.position);
        ghost.home.Enable(duration);
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
        eaten = false;
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
