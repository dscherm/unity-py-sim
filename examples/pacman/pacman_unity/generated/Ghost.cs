using UnityEngine;
[RequireComponent(typeof(GhostChase))]
[RequireComponent(typeof(GhostFrightened))]
[RequireComponent(typeof(GhostHome))]
[RequireComponent(typeof(GhostScatter))]
[RequireComponent(typeof(Movement))]
public class Ghost : MonoBehaviour
{
    public int points = 200;
    public Movement movement;
    public GhostHome home;
    public GhostScatter scatter;
    public GhostChase chase;
    public GhostFrightened frightened;
    public object initialBehavior;
    public object target;
    public static int PACMAN_LAYER = 7;
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
        frightened.Disable();
        chase.Disable();
        scatter.Enable();
        if (home != initialBehavior)
        {
            home.Disable();
        }
        if (initialBehavior != null)
        {
            initialBehavior.Enable();
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
