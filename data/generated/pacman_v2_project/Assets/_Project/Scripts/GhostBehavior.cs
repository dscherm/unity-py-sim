using UnityEngine;
namespace PacmanV2
{
    [RequireComponent(typeof(Ghost))]
    public class GhostBehavior : MonoBehaviour
    {
        public float duration = 0.0f;
        [SerializeField] protected Ghost ghost;
         void Awake()
        {
            ghost = GetComponent<Ghost>();
        }
        public void Enable(float duration = -1.0f)
        {
            enabled = true;
            if (duration < 0)
            {
                duration = this.duration;
            }
            CancelInvoke();
            Invoke("Disable", duration);
        }
        public void Disable()
        {
            enabled = false;
            CancelInvoke();
        }
    }
}
