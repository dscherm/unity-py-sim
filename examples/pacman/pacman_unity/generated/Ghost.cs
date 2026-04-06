using UnityEngine;
[RequireComponent(typeof(GhostChase))]
[RequireComponent(typeof(GhostFrightened))]
[RequireComponent(typeof(GhostHome))]
[RequireComponent(typeof(GhostScatter))]
[RequireComponent(typeof(Movement))]
public class Ghost : MonoBehaviour
{
    public static int PACMAN_LAYER = 7;
    public static Movement movement = null;
    public static GhostHome home = null;
    public static GhostScatter scatter = null;
    public static GhostChase chase = null;
    public static GhostFrightened frightened = null;
    public static object initialBehavior = null;
    public static object target = null;
    public static int points = 200;
     void Awake()
    {
        movement = GetComponent<Movement>();
    }
     void Start()
    {
        home = GetComponent<GhostHome>();
        scatter = GetComponent<GhostScatter>();
        chase = GetComponent<GhostChase>();
        frightened = GetComponent<GhostFrightened>();
        ResetState();
    }
    public void ResetState()
    {
        gameObject.SetActive(true);
        movement.ResetState();
        frightened.DisableBehavior();
        chase.DisableBehavior();
        scatter.EnableBehavior();
        if (home != initialBehavior)
        {
            home.DisableBehavior();
        }
        if (initialBehavior != null)
        {
            initialBehavior.EnableBehavior();
        }
    }
    public void SetPosition(Vector2 position)
    {
        transform.position = position;
    }
     void OnCollisionEnter2D(Collision2D collision)
    {
        var go = getattr(collision, "gameObject", collision);
        if (go != null && go.layer == PACMAN_LAYER)
        {
            if (GameManager.instance != null)
            {
                if (frightened.enabled)
                {
                    GameManager.instance.GhostEaten(this);
                }
                else
                {
                    GameManager.instance.PacmanEaten();
                }
            }
        }
    }
}
