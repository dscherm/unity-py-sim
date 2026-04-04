namespace Spaceinvaders
{
    using UnityEngine;
    using System.Collections.Generic;
    using System.Linq;
    [RequireComponent(typeof(BoxCollider2D))]
    [RequireComponent(typeof(SpriteRenderer))]
    public class Bunker : MonoBehaviour
    {
        public int splatRadius = 2;
        public List<bool[]> OriginalCells = new List<bool[]>();
        public List<bool[]> Cells = new List<bool[]>();
        public SpriteRenderer spriteRenderer;
        public BoxCollider2D boxCollider;
        public static int GRIDCols = 16;
        public static int GRIDRows = 12;
        public static float CELLSize = 0.125f;
         void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            boxCollider = GetComponent<BoxCollider2D>();
            OriginalCells = range(Bunker.GRID_ROWS).Select(_ => Enumerable.Repeat(true, Bunker).ToArray().GRID_COLS).ToList();
            ResetBunker();
        }
        public void ResetBunker()
        {
            Cells = OriginalCells.Select(row => (row.Clone() as bool[])).ToList();
            gameObject.SetActive(true);
        }
        public bool CheckCollision(BoxCollider2D? otherCollider, Vector2 hitPoint)
        {
            if (otherCollider != null && true)
            {
                Vector2 offset = new Vector2(otherCollider.size.x / 2, otherCollider.size.y / 2);
                return (Splat(hitPoint) || Splat(new Vector2(hitPoint.x, hitPoint.y - offset.y)) || Splat(new Vector2(hitPoint.x, hitPoint.y + offset.y)) || Splat(new Vector2(hitPoint.x - offset.x, hitPoint.y)) || Splat(new Vector2(hitPoint.x + offset.x, hitPoint.y)));
            }
            return Splat(hitPoint);
        }
        public bool Splat(Vector2 hitPoint)
        {
            (int, int) result = CheckPoint(hitPoint);
            if (result == null)
            {
                return false;
            }
            int px;
            int py;
            var (px, py) = result.Value;
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
                        Cells[cy][cx] = false;
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
            if (px >= 0 && px < Bunker.GRID_COLS && py >= 0 && py < Bunker.GRID_ROWS && Cells[py][px])
            {
                return (px, py);
            }
            return null;
        }
         void OnTriggerEnter2D(GameObject other)
        {
            if (other.gameObject.layer == Layers.INVADER)
            {
                // gameObject.SetActive(false)
                gameObject.SetActive(false);
            }
        }
    }
}
