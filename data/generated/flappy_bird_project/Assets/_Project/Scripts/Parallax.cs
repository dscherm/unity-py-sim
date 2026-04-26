using UnityEngine;
namespace FlappyBird
{
    public class Parallax : MonoBehaviour
    {
        public float animationSpeed = 1.0f;
        public float wrapWidth = 20.0f;
        public float startX = 0.0f;
         void Awake()
        {
            startX = transform.position.x;
        }
         void Update()
        {
            var pos = transform.position;
            var newX = pos.x - animationSpeed * Time.deltaTime;
            if (newX < startX - wrapWidth)
            {
                newX += wrapWidth;
            }
            transform.position = new Vector3(newX, pos.y, pos.z);
        }
    }
}
