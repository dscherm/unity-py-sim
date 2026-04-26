using UnityEngine;

// Scaffolder fixture (data/lessons/flappy_bird_deploy.md gap 5).
// Letterboxes Main Camera to a target aspect so sprite art painted
// for one aspect doesn't stretch/crop when Unity's Game view uses
// a different window shape.
[RequireComponent(typeof(Camera))]
[DisallowMultipleComponent]
public class AspectLock : MonoBehaviour
{
    [Tooltip("Target width/height ratio. 9/16 = portrait (Flappy Bird). 16/9 = landscape.")]
    public float targetAspect = 9f / 16f;

    Camera cam;
    int lastW, lastH;

    void Awake()
    {
        cam = GetComponent<Camera>();
        Apply();
    }

    void Update()
    {
        if (Screen.width != lastW || Screen.height != lastH) Apply();
    }

    void Apply()
    {
        if (cam == null) return;
        lastW = Screen.width; lastH = Screen.height;
        float windowAspect = (float)Screen.width / Screen.height;
        float scaleHeight = windowAspect / targetAspect;
        if (scaleHeight < 1f)
        {
            // Window wider than target — letterbox top/bottom.
            var r = cam.rect;
            r.width = 1f;
            r.height = scaleHeight;
            r.x = 0f;
            r.y = (1f - scaleHeight) / 2f;
            cam.rect = r;
        }
        else
        {
            // Window narrower than target — pillarbox left/right.
            float scaleWidth = 1f / scaleHeight;
            var r = cam.rect;
            r.width = scaleWidth;
            r.height = 1f;
            r.x = (1f - scaleWidth) / 2f;
            r.y = 0f;
            cam.rect = r;
        }
    }
}
