using UnityEngine;
namespace PacmanV2
{
    public class GhostFrightened : GhostBehavior
    {
        public bool eaten = false;
        public Sprite blueSprite = null;
        public Sprite whiteSprite = null;
        public SpriteRenderer bodySr = null;
        public Sprite originalSprite = null;
        public SpriteRenderer eyesSr = null;
        public AnimatedSprite bodyAnim = null;
        public void Enable(float duration = -1.0f)
        {
            base.Enable(duration);
            eaten = false;
            if (bodyAnim == null && ghost != null)
            {
                bodyAnim = ghost.gameObject.GetComponent<AnimatedSprite>();
            }
            if (bodyAnim != null)
            {
                bodyAnim.enabled = false;
            }
            if (bodySr == null && ghost != null)
            {
                bodySr = ghost.gameObject.GetComponent<SpriteRenderer>();
            }
            if (bodySr != null && blueSprite != null)
            {
                originalSprite = bodySr.sprite;
                bodySr.sprite = blueSprite;
                // Ensure the renderer is visible (AnimatedSprite.on_disable hides it)
                bodySr.enabled = true;
            }
            if (ghost != null && ghost.eyes != null)
            {
                var eyesSr = ghost.eyes.GetComponent<SpriteRenderer>();
                if (eyesSr != null)
                {
                    this.eyesSr = eyesSr;
                    eyesSr.enabled = false;
                }
            }
            if (duration > 0)
            {
                CancelInvoke("flash");
                Invoke("flash", duration / 2);
            }
        }
        public void Disable()
        {
            base.Disable();
            eaten = false;
            if (bodySr != null && originalSprite != null)
            {
                bodySr.sprite = originalSprite;
            }
            if (bodyAnim != null)
            {
                bodyAnim.enabled = true;
            }
            if (eyesSr != null)
            {
                eyesSr.enabled = true;
            }
            CancelInvoke("flash");
        }
        public void Flash()
        {
            if (bodySr != null && whiteSprite != null)
            {
                bodySr.sprite = whiteSprite;
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
            var otherGo = other.gameObject;
            var node = otherGo.GetComponent<Node>();
            if (node == null || !enabled)
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
            var maxDist = -1.0f;
            foreach (var d in available)
            {
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
                if (dist > maxDist)
                {
                    maxDist = dist;
                    bestDir = d;
                }
            }
            movement.SetDirection(bestDir);
        }
        public void Eat()
        {
            eaten = true;
            if (ghost != null)
            {
                // Teleport to home position
                if (ghost.home != null && ghost.home.inside != null)
                {
                    var homePos = ghost.home.inside.transform.position;
                    ghost.gameObject.transform.position = new Vector2(homePos.x, homePos.y);
                    if (ghost.movement != null && ghost.movement.rb != null)
                    {
                        ghost.movement.rb.MovePosition(new Vector2(homePos.x, homePos.y));
                    }
                    ghost.home.Enable();
                }
                Disable();
            }
        }
    }
}
