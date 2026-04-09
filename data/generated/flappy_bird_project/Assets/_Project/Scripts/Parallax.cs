using UnityEngine;
public class Parallax : MonoBehaviour
{
    public float animationSpeed = 1.0f;
    public float wrapWidth = 20.0f;
    public float StartX = 0.0f;
     void Awake()
    {
        StartX = transform.position.x;
    }
     void Update()
    {
        var pos = transform.position;
        var newX = pos.x - animationSpeed * Time.deltaTime;
        if (newX < StartX - wrapWidth)
        {
            newX += wrapWidth;
        }
        transform.position = new Vector3(newX, pos.y, pos.z);
    }
}
