using UnityEngine;
[RequireComponent(typeof(Ghost))]
public class GhostBehavior : MonoBehaviour
{
    public float duration = 0.0f;
    [SerializeField] private Ghost ghost;
    public bool enabled;
     void Awake()
    {
        ghost = GetComponent<Ghost>();
    }
    public void Enable(float duration)
    {
        enabled = true;
        if (duration < 0)
        {
            var duration = this.duration;
        }
        CancelInvoke();
        invoke("Disable", duration);
    }
    public void Disable()
    {
        enabled = false;
        CancelInvoke();
    }
}
