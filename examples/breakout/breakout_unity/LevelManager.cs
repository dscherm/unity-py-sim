using UnityEngine;

public class LevelManager : MonoBehaviour
{
    [SerializeField] private GameObject brickPrefab;
    [SerializeField] private int columns = 10;
    [SerializeField] private int rows = 8;
    [SerializeField] private float brickWidth = 1.3f;
    [SerializeField] private float brickHeight = 0.5f;
    [SerializeField] private float gap = 0.1f;
    [SerializeField] private float startY = 4.5f;

    private static readonly Color[] RowColors = {
        new Color(0.86f, 0.20f, 0.20f), // red
        new Color(0.86f, 0.20f, 0.20f),
        new Color(0.86f, 0.55f, 0.16f), // orange
        new Color(0.86f, 0.55f, 0.16f),
        new Color(0.20f, 0.71f, 0.20f), // green
        new Color(0.20f, 0.71f, 0.20f),
        new Color(0.20f, 0.47f, 0.86f), // blue
        new Color(0.20f, 0.47f, 0.86f),
    };

    private static readonly int[] RowPoints = { 30, 30, 20, 20, 10, 10, 10, 10 };

    void Start()
    {
        float gridWidth = columns * (brickWidth + gap) - gap;
        float startX = -gridWidth / 2f + brickWidth / 2f;

        for (int row = 0; row < rows; row++)
        {
            for (int col = 0; col < columns; col++)
            {
                float x = startX + col * (brickWidth + gap);
                float y = startY - row * (brickHeight + gap);
                Vector2 pos = new Vector2(x, y);

                GameObject brick = Instantiate(brickPrefab, pos, Quaternion.identity);
                brick.tag = "Brick";

                var sr = brick.GetComponent<SpriteRenderer>();
                if (sr != null && row < RowColors.Length)
                    sr.color = RowColors[row];

                var brickComp = brick.GetComponent<Brick>();
                if (brickComp != null && row < RowPoints.Length)
                    brickComp.points = RowPoints[row];
            }
        }
    }
}
