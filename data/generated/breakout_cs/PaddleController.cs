namespace breakout
{
    using UnityEngine;
    using UnityEngine.InputSystem;
    [RequireComponent(typeof(Rigidbody2D))]
    public class PaddleController : MonoBehaviour
    {
        public float speed = 12f;
        public float boundX = 6.5f;
        public bool ballAttached = true;
         void Start()
        {
            rb = GetComponent<Rigidbody2D>();
            rb.SyncFromTransform();
        }
         void Update()
        {
            float inputVal = /* TODO: use InputAction for Horizontal axis */ 0f;
            if (Mathf.Abs(inputVal) > 0.01f)
            {
                Vector2 pos = transform.position;
                float newX = pos.x + inputVal * speed * Time.deltaTime;
                newX = Mathf.Max(-boundX, Mathf.Min(boundX, newX));
                transform.position = new Vector2(newX, pos.y);
                rb.MovePosition(new Vector2(newX, pos.y));
            }
        }
        public void LaunchBall()
        {
            ballAttached = false;
        }
    }
}
