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
        sprite_renderer = GetComponent<SpriteRenderer>();
        box_collider = GetComponent<BoxCollider2D>();
        _original_cells = range(GRID_ROWS).Select( => [true] * GRIDCOLS).ToList();
        reset_bunker();
    }
    public void ResetBunker()
    {
        _cells = _original_cells.Select(row => row[:]).ToList();
        game_object.active = true;
    }
    public void CheckCollision(object otherCollider, object hitPoint)
    {
        if (other_collider && hasattr(other_collider, "size"))
        {
            Vector2 offset = new Vector2(other_collider.size.x / 2, other_collider.size.y / 2);
            return (_splat(hit_point) or;
            {
                    _splat(new Vector2(hit_point.x, hit_point.y - offset.y)) or;
                    _splat(new Vector2(hit_point.x, hit_point.y + offset.y)) or;
                    _splat(new Vector2(hit_point.x - offset.x, hit_point.y)) or;
                    _splat(new Vector2(hit_point.x + offset.x, hit_point.y)));
            }
        }
        return _splat(hit_point);
    }
    public void Splat(object hitPoint)
    {
        var result = _check_point(hit_point);
        if (result == null)
        {
            return false;
        }
        px, py = result;
        px -= splat_radius;
        py -= splat_radius;
        for (int y = 0; y < splat_radius * 2; y++)
        {
            for (int x = 0; x < splat_radius * 2; x++)
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
        if (box_collider == null)
        {
            return null;
        }
        var pos = transform.position;
        var local_x = hit_point.x - pos.x;
        var local_y = hit_point.y - pos.y;
        var bw = box_collider.size.x;
        var bh = box_collider.size.y;
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
