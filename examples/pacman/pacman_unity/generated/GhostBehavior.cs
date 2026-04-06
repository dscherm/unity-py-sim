using System.Collections;
using UnityEngine;
[RequireComponent(typeof(Ghost))]
public class GhostBehavior : MonoBehaviour
{
    public bool enabled;
    public static Ghost ghost = null;
    public static float duration = 0.0f;
    public static object DurationCoroutine = null;
     void Start()
    {
        ghost = GetComponent<Ghost>();
    }
    public void EnableBehavior(float duration)
    {
        enabled = true;
        if (duration < 0)
        {
            var duration = duration;
        }
        if (DurationCoroutine != null)
        {
            DurationCoroutine = null;
        }
        if (duration > 0)
        {
            DurationCoroutine = StartCoroutine( DisableAfter(duration) );
        }
    }
    public void DisableBehavior()
    {
        enabled = false;
        DurationCoroutine = null;
    }
    public IEnumerator DisableAfter(float duration)
    {
        yield return new WaitForSeconds(duration);
        DisableBehavior();
    }
}
