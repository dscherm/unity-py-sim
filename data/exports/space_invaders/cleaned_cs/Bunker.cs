using UnityEngine;
using System.Linq;
[RequireComponent(typeof(BoxCollider2D))]
[RequireComponent(typeof(SpriteRenderer))]
public class Bunker : MonoBehaviour
{
    [SerializeField] private int splatRadius = 2;
    [SerializeField] private bool[][] OriginalCells = [];
    [SerializeField] private bool[][] Cells = [];
    private SpriteRenderer? spriteRenderer;
    private BoxCollider2D? boxCollider;
     void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
        boxCollider = GetComponent<BoxCollider2D>();
        _originalCells = range(GRID_ROWS).Select( => [true] * GRIDCOLS).ToList();
        resetBunker();
    }
    public void ResetBunker()
    {
        _cells = _originalCells.Select(row => row[:]).ToList();
        game_object.active = true;
    }
    public void CheckCollision(object otherCollider, object hitPoint)
    {
        if (other_collider && hasattr(other_collider, "size"))
        {
            Vector2 offset = new Vector2(other_collider.size.x / 2, other_collider.size.y / 2);
            return (Splat(hit_point) or;
            {
                    Splat(new Vector2(hit_point.x, hit_point.y - offset.y)) or;
                    Splat(new Vector2(hit_point.x, hit_point.y + offset.y)) or;
                    Splat(new Vector2(hit_point.x - offset.x, hit_point.y)) or;
                    Splat(new Vector2(hit_point.x + offset.x, hit_point.y)));
            }
        }
        return Splat(hit_point);
    }
    public void Splat(object hitPoint)
    {
        var result = CheckPoint(hit_point);
        if (result == null)
        {
            return false;
        }
        px, py = result;
        px -= splatRadius;
        py -= splatRadius;
        for (int y = 0; y < splatRadius * 2; y++)
        {
            for (int x = 0; x < splatRadius * 2; x++)
            {
                cx, cy = px + x, py + y;
                if (0 <= cy < GRID_ROWS && 0 <= cx < GRID_COLS)
                {
                    _cells[cy][cx] = false;
                }
            }
        }
        return true;
    }
    public void CheckPoint(object hitPoint)
    {
        if (boxCollider == null)
        {
            return null;
        }
        var pos = transform.position;
        var local_x = hit_point.x - pos.x;
        var local_y = hit_point.y - pos.y;
        var bw = boxCollider.size.x;
        var bh = boxCollider.size.y;
        local_x += bw / 2;
        local_y += bh / 2;
        var px = int(local_x / bw * GRID_COLS);
        var py = int(local_y / bh * GRID_ROWS);
        if (0 <= px < GRID_COLS && 0 <= py < GRID_ROWS && _cells[py][px])
        {
            return (px, py);
        }
        return null;
    }
     void OnTriggerEnter2D(Collider2D other)
    {
        if (other.layer == LAYER_INVADER)
        {
            // gameObject.SetActive(false)
            game_object.active = false;
        }
    }
}
