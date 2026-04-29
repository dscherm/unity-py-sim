using UnityEngine.InputSystem;
using UnityEngine;
namespace Pong
{
    [RequireComponent(typeof(Rigidbody2D))]
    public class PaddleController : MonoBehaviour
    {
        public float speed = 10.0f;
        public float boundY = 4.0f;
        public string inputAxis = "Vertical";
        [SerializeField] private Rigidbody2D rb;
         void Start()
        {
            rb = GetComponent<Rigidbody2D>();
        }
         void Update()
        {
            float inputVal = Input.GetAxis(inputAxis);
            if (Mathf.Abs(inputVal) > 0.01f)
            {
                var pos = transform.position;
                var newY = pos.y + inputVal * speed * Time.deltaTime;
                newY = Mathf.Max(-boundY, Mathf.Min(boundY, newY));
                transform.position = new Vector2(pos.x, newY);
                rb.MovePosition(new Vector2(pos.x, newY));
            }
        }
    }
}
