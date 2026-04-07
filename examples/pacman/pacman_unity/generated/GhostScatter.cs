using UnityEngine;
public class GhostScatter : GhostBehavior
{
     void OnDisable()
    {
        if (ghost != null && ghost.chase != null && ghost.chase.enabled != null)
        {
            ghost.chase.Enable();
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
            var dirs = node.availableDirections;
            if (!dirs)
            {
                return;
            }
            // Pick a random available direction
            var index = Random.Range(0, dirs.Count - 1);
            // Prefer not to go back the same direction so increment the
            // index to the next available direction
            if (dirs.Count > 1)
            {
                Vector2 reverse = new Vector2( -ghost.movement.direction.x, -ghost.movement.direction.y);
                if ((dirs[index].x == reverse.x && dirs[index].y == reverse.y))
                {
                    index = (index + 1) % dirs.Count;
                }
            }
            ghost.movement.SetDirection(dirs[index]);
        }
    }
}
