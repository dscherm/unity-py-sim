using UnityEngine.InputSystem;
using UnityEngine;
namespace Breakout
{
    [RequireComponent(typeof(Rigidbody2D))]
    public class PaddleController : MonoBehaviour
    {
        public float speed = 12.0f;
        public float boundX = 6.5f;
        public bool ballAttached = true;
        [SerializeField] private Rigidbody2D rb;
         void Start()
        {
            rb = GetComponent<Rigidbody2D>();
        }
         void Update()
        {
            float inputVal = ((Keyboard.current.dKey.isPressed ? 1f : 0f) - (Keyboard.current.aKey.isPressed ? 1f : 0f));
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
