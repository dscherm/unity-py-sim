using UnityEngine;
[RequireComponent(typeof(GhostChase))]
[RequireComponent(typeof(GhostEyes))]
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
    public GhostEyes eyes;
    public object initialBehavior;
    public GameObject target;
    public static int PACMAN_LAYER = 3;
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
        foreach (var child in transform.children)
        {
            var eyes = child.gameObject.GetComponent<GhostEyes>();
            if (eyes != null)
            {
                eyes = eyes;
                break;
            }
        }
        ResetState();
    }
    public void ResetState()
    {
        gameObject.SetActive(true);
        if (movement != null)
        {
            movement.ResetState();
        }
        if (frightened != null)
        {
            frightened.Disable();
        }
        if (chase != null)
        {
            chase.Disable();
        }
        if (scatter != null)
        {
            scatter.Enable();
        }
        if (home != initialBehavior)
        {
            if (home != null)
            {
                home.Disable();
            }
        }
        if (initialBehavior != null)
        {
            initialBehavior.Enable();
        }
    }
     void OnCollisionEnter2D(Collision2D collision)
    {
        var otherGo = getattr(collision, "gameObject", collision);
        if (otherGo.layer == PACMAN_LAYER)
        {
            if (frightened != null && frightened.enabled && frightened.eaten == null)
            {
                // Ghost is eaten by Pacman
                if (GameManager.instance != null)
                {
                    GameManager.instance.GhostEaten(this);
                }
            }
            else
            {
                // Pacman is eaten by ghost
                if (GameManager.instance != null)
                {
                    GameManager.instance.PacmanEaten();
                }
            }
        }
    }
}
