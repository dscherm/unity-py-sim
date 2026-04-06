using UnityEngine;
public class Passage : MonoBehaviour
{
    public static Transform connection = null;
     void OnTriggerEnter2D(Collider2D other)
    {
        Vector2 position = new Vector2( connection.position.x, connection.position.y);
        other.transform.position = position;
    }
}
