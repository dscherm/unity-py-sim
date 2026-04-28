using System.Collections.Generic;
using System.Linq;
using UnityEngine;
namespace SpaceInvaders
{
    [RequireComponent(typeof(BoxCollider2D))]
    [RequireComponent(typeof(SpriteRenderer))]
    public class Bunker : MonoBehaviour
    {
        public int splatRadius = 2;
        public List<bool[]> originalCells = new List<bool[]>();
        public List<bool[]> cells = new List<bool[]>();
        public SpriteRenderer spriteRenderer;
        public BoxCollider2D boxCollider;
        public static int GRID_COLS = 16;
        public static int GRID_ROWS = 12;
        public static float CELL_SIZE = 0.125f;
         void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            boxCollider = GetComponent<BoxCollider2D>();
            originalCells = Enumerable.Range(0, Bunker.GRID_ROWS).Select(_ => Enumerable.Repeat(true, Bunker.GRID_COLS).ToArray()).ToList();
            ResetBunker();
        }
        public void ResetBunker()
        {
            cells = originalCells.Select(row => (row.Clone() as bool[])).ToList();
            gameObject.SetActive(true);
        }
        public bool CheckCollision(BoxCollider2D? otherCollider, Vector2 hitPoint)
        {
            if (otherCollider != null)
            {
                Vector2 offset = new Vector2(otherCollider.size.x / 2, otherCollider.size.y / 2);
                return (Splat(hitPoint) || Splat(new Vector2(hitPoint.x, hitPoint.y - offset.y)) || Splat(new Vector2(hitPoint.x, hitPoint.y + offset.y)) || Splat(new Vector2(hitPoint.x - offset.x, hitPoint.y)) || Splat(new Vector2(hitPoint.x + offset.x, hitPoint.y)));
            }
            return Splat(hitPoint);
        }
        public bool Splat(Vector2 hitPoint)
        {
            (int, int)? result = CheckPoint(hitPoint);
            if (result == null)
            {
                return false;
            }
            int px;
            int py;
            (px, py) = result.Value;
            px -= splatRadius;
            py -= splatRadius;
            for (int y = 0; y < splatRadius * 2; y++)
            {
                for (int x = 0; x < splatRadius * 2; x++)
                {
                    int cx = px + x;
                    int cy = py + y;
                    if (cy >= 0 && cy < Bunker.GRID_ROWS && cx >= 0 && cx < Bunker.GRID_COLS)
                    {
                        cells[cy][cx] = false;
                    }
                }
            }
            return true;
        }
        public (int, int)? CheckPoint(Vector2 hitPoint)
        {
            if (boxCollider == null)
            {
                return null;
            }
            Vector2 pos = transform.position;
            float localX = hitPoint.x - pos.x;
            float localY = hitPoint.y - pos.y;
            float bw = boxCollider.size.x;
            float bh = boxCollider.size.y;
            localX += bw / 2;
            localY += bh / 2;
            int px = (int)(localX / bw * Bunker.GRID_COLS);
            int py = (int)(localY / bh * Bunker.GRID_ROWS);
            if (px >= 0 && px < Bunker.GRID_COLS && py >= 0 && py < Bunker.GRID_ROWS && cells[py][px])
            {
                return (px, py);
            }
            return null;
        }
         void OnTriggerEnter2D(Collider2D other)
        {
            if (other.gameObject.layer == Layers.INVADER)
            {
                // gameObject.SetActive(false)
                gameObject.SetActive(false);
            }
        }
    }
}
