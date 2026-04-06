using UnityEngine;
[RequireComponent(typeof(Movement))]
[RequireComponent(typeof(SpriteRenderer))]
public class GhostEyes : MonoBehaviour
{
    public static string upRef = "ghost_eyes_up";
    public static string downRef = "ghost_eyes_down";
    public static string leftRef = "ghost_eyes_left";
    public static string rightRef = "ghost_eyes_right";
    public static SpriteRenderer spriteRenderer = null;
    public static Movement movement = null;
     void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
        movement = gameObject.GetComponent<Movement>();
        if (movement == null && transform.parent != null)
        {
            var parentGo = transform.parent.gameObject;
            if (parentGo != null)
            {
                movement = parentGo.GetComponent<Movement>();
            }
        }
    }
     void Update()
    {
        if (spriteRenderer == null || movement == null)
        {
            return;
        }
        var d = movement.direction;
    }
}
