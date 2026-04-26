using UnityEngine;
public class Pipes : MonoBehaviour
{
    public float speed = 5.0f;
    public float gap = 3.0f;
    public float leftEdge = 0.0f;
    public Transform top;
    public Transform bottom;
     void Start()
    {
        if (Camera.main != null)
        {
            // Camera.main.ScreenToWorldPoint(Vector3.zero).x - 1f
            var worldPoint = Camera.main.ScreenToWorldPoint(Vector3.zero);
            leftEdge = worldPoint.x - 1.0f;
        }
        else
        {
            leftEdge = -10.0f;
        }
        if (top != null)
        {
            top.position = top.position + Vector3.up * (gap / 2);
        }
        if (bottom != null)
        {
            bottom.position = bottom.position + Vector3.down * (gap / 2);
        }
    }
     void Update()
    {
        transform.position = transform.position + Vector3.left * (speed * Time.deltaTime);
        if (transform.position.x < leftEdge)
        {
            Destroy(gameObject);
        }
    }
}
