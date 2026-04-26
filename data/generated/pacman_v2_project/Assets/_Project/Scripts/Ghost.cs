using UnityEngine;
namespace PacmanV2
{
    [RequireComponent(typeof(GhostChase))]
    [RequireComponent(typeof(GhostEyes))]
    [RequireComponent(typeof(GhostFrightened))]
    [RequireComponent(typeof(GhostHome))]
    [RequireComponent(typeof(GhostScatter))]
    [RequireComponent(typeof(Movement))]
    public class Ghost : MonoBehaviour
    {
    [SerializeField] private GameManager gameManager;
        public int points = 200;
        public Movement movement;
        public GhostHome home;
        public GhostScatter scatter;
        public GhostChase chase;
        public GhostFrightened frightened;
        public GhostEyes eyes;
        [SerializeField] private GhostBehavior initialBehavior;
        public GameObject target;
        public static int PACMAN_LAYER = 3;
         void Awake()
        {
        if (gameManager == null) gameManager = FindObjectOfType<GameManager>();
            movement = GetComponent<Movement>();
        }
         void Start()
        {
            home = GetComponent<GhostHome>();
            scatter = GetComponent<GhostScatter>();
            chase = GetComponent<GhostChase>();
            frightened = GetComponent<GhostFrightened>();
            foreach (Transform child in transform)
            {
                var eyes = child.gameObject.GetComponent<GhostEyes>();
                if (eyes != null)
                {
                    this.eyes = eyes;
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
            var otherGo = collision.gameObject;
            if (otherGo.layer == PACMAN_LAYER)
            {
                if (frightened != null && frightened.enabled && !frightened.eaten)
                {
                    // Ghost is eaten by Pacman
                    if (gameManager != null)
                    {
                        gameManager.GhostEaten(this);
                    }
                }
                else
                {
                    // Pacman is eaten by ghost
                    if (gameManager != null)
                    {
                        gameManager.PacmanEaten();
                    }
                }
            }
        }
    }
}
