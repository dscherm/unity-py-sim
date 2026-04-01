using UnityEngine;

// Unity APIs used: MonoBehaviour, Rigidbody2D, Vector2, OnCollisionEnter2D, Collision2D
public class BallController : MonoBehaviour
{
    [SerializeField] private float initialSpeed = 8f;
    [SerializeField] private float speedIncrease = 0.5f;

    private Rigidbody2D rb;
    private float currentSpeed;

    void Start()
    {
        rb = GetComponent<Rigidbody2D>();
        currentSpeed = initialSpeed;
        Launch();
    }

    public void Launch()
    {
        float xDir = Random.value > 0.5f ? 1f : -1f;
        float yDir = Random.Range(-0.5f, 0.5f);
        Vector2 direction = new Vector2(xDir, yDir).normalized;
        rb.velocity = direction * currentSpeed;
    }

    public void Reset()
    {
        transform.position = Vector2.zero;
        rb.velocity = Vector2.zero;
        currentSpeed = initialSpeed;
    }

    void OnCollisionEnter2D(Collision2D collision)
    {
        if (collision.gameObject.tag == "Paddle")
        {
            currentSpeed += speedIncrease;

            // Reflect with slight angle variation based on hit position
            float hitY = transform.position.y - collision.transform.position.y;
            float normalizedHit = hitY / 1f; // Paddle half-height
            Vector2 dir = new Vector2(rb.velocity.x > 0 ? -1 : 1, normalizedHit).normalized;
            rb.velocity = dir * currentSpeed;
        }
    }
}
