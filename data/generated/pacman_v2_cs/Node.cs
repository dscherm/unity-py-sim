using System.Collections.Generic;
using UnityEngine;
public class Node : MonoBehaviour
{
    private const int OBSTACLE_LAYER = 6;
    public int obstacleLayer = OBSTACLE_LAYER;
    public List<Vector2> availableDirections;
     void Start()
    {
        availableDirections.Clear();
        CheckDirection(new Vector2(0, 1));
        CheckDirection(new Vector2(0, -1));
        CheckDirection(new Vector2(-1, 0));
        CheckDirection(new Vector2(1, 0));
    }
    public void CheckDirection(Vector2 direction)
    {
        var pos = transform.position;
        Vector2 checkPos = new Vector2( pos.x + direction.x * 1.0f, pos.y + direction.y * 1.0f);
        var hit = Physics2D.OverlapBox( point=checkPos, new Vector2(0.5f, 0.5f), 0.0f, 1 << obstacleLayer);
        if (hit == null)
        {
            availableDirections.Add(direction);
        }
    }
}
