using UnityEngine;

public class PaddleController : MonoBehaviour
{
    [SerializeField] private float speed = 12f;
    [SerializeField] private float boundX = 6.5f;

    private Rigidbody2D rb;
    private bool ballAttached = true;

    void Start()
    {
        rb = GetComponent<Rigidbody2D>();
    }

    void Update()
    {
        float input = Input.GetAxis("Horizontal");
        if (Mathf.Abs(input) > 0.01f)
        {
            Vector2 pos = transform.position;
            float newX = Mathf.Clamp(pos.x + input * speed * Time.deltaTime, -boundX, boundX);
            transform.position = new Vector2(newX, pos.y);
            rb.MovePosition(new Vector2(newX, pos.y));
        }
    }

    public void LaunchBall()
    {
        ballAttached = false;
    }
}
