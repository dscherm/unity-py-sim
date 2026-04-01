using UnityEngine;

// Unity APIs used: MonoBehaviour, Rigidbody2D, Input.GetAxis, Vector2, Time.fixedDeltaTime
public class PaddleController : MonoBehaviour
{
    [SerializeField] private float speed = 10f;
    [SerializeField] private float boundY = 4f;
    [SerializeField] private string inputAxis = "Vertical";

    private Rigidbody2D rb;

    void Start()
    {
        rb = GetComponent<Rigidbody2D>();
    }

    void FixedUpdate()
    {
        float input = Input.GetAxis(inputAxis);
        Vector2 velocity = new Vector2(0, input * speed);
        rb.velocity = velocity;

        // Clamp position
        Vector2 pos = transform.position;
        if (pos.y > boundY)
        {
            transform.position = new Vector2(pos.x, boundY);
            rb.velocity = Vector2.zero;
        }
        else if (pos.y < -boundY)
        {
            transform.position = new Vector2(pos.x, -boundY);
            rb.velocity = Vector2.zero;
        }
    }
}
