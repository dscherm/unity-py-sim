namespace Breakout
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
            rb: Rigidbody2D = GetComponent<Rigidbody2D>();
            rb.SyncFromTransform();
        }
         void Update()
        {
            input_val: float = /* TODO: use InputAction for Horizontal axis */ 0f;
            if (Mathf.Abs(input_val) > 0.01f)
            {
                pos: Vector2 = transform.position;
                newX: float = pos.x + input_val * speed * Time.deltaTime;
                var newX = Mathf.Max(-boundX, Mathf.Min(boundX, newX));
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
