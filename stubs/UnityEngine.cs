// Minimal UnityEngine stubs for compilation gate.
// Just enough to make generated C# compile — not functional.

namespace UnityEngine
{
    public class Object
    {
        public string name;
        public static void Destroy(Object obj, float t = 0f) { }
        public static void DontDestroyOnLoad(Object obj) { }
        public static T Instantiate<T>(T original) where T : Object => default;
        public static T Instantiate<T>(T original, Vector3 position, Quaternion rotation) where T : Object => default;
        public static GameObject Instantiate(GameObject original, Vector3 position, Quaternion rotation) => default;
    }

    public class Component : Object
    {
        public GameObject gameObject;
        public Transform transform;
        public T GetComponent<T>() where T : Component => default;
        public T[] GetComponentsInChildren<T>() where T : Component => default;
        public T AddComponent<T>() where T : Component => default;
    }

    public class Behaviour : Component
    {
        public bool enabled;
    }

    public class MonoBehaviour : Behaviour
    {
        public Coroutine StartCoroutine(System.Collections.IEnumerator routine) => null;
        public void StopCoroutine(Coroutine routine) { }
        public void StopAllCoroutines() { }
        public void Invoke(string methodName, float time) { }
        public void CancelInvoke(string methodName) { }
        public bool IsInvoking(string methodName) => false;
    }

    public class GameObject : Object
    {
        public bool activeSelf;
        public bool activeInHierarchy;
        public string tag;
        public int layer;
        public Transform transform;

        public GameObject() { }
        public GameObject(string name) { }

        public T GetComponent<T>() where T : Component => default;
        public T AddComponent<T>() where T : Component => default;
        public void SetActive(bool value) { }

        public static GameObject Find(string name) => null;
        public static GameObject FindWithTag(string tag) => null;
        public static GameObject[] FindGameObjectsWithTag(string tag) => new GameObject[0];
    }

    public class Transform : Component
    {
        public Vector3 position;
        public Vector3 localPosition;
        public Quaternion rotation;
        public Quaternion localRotation;
        public Vector3 localScale;
        public Transform parent;
        public int childCount;

        public Transform GetChild(int index) => null;
        public void SetParent(Transform parent) { }
        public void Translate(Vector3 translation) { }
        public void Rotate(Vector3 eulers) { }
    }

    public struct Vector2
    {
        public float x, y;
        public float magnitude;
        public float sqrMagnitude;
        public Vector2 normalized => default;

        public Vector2(float x, float y) { this.x = x; this.y = y; magnitude = 0; sqrMagnitude = 0; }

        public static Vector2 zero => new Vector2(0, 0);
        public static Vector2 one => new Vector2(1, 1);
        public static Vector2 up => new Vector2(0, 1);
        public static Vector2 down => new Vector2(0, -1);
        public static Vector2 left => new Vector2(-1, 0);
        public static Vector2 right => new Vector2(1, 0);

        public static Vector2 operator +(Vector2 a, Vector2 b) => default;
        public static Vector2 operator -(Vector2 a, Vector2 b) => default;
        public static Vector2 operator *(Vector2 a, float d) => default;
        public static Vector2 operator *(float d, Vector2 a) => default;
        public static float Distance(Vector2 a, Vector2 b) => 0f;

        // Unity has implicit conversion between Vector2 and Vector3
        public static implicit operator Vector2(Vector3 v) => new Vector2(v.x, v.y);
        public static implicit operator Vector3(Vector2 v) => new Vector3(v.x, v.y, 0);
    }

    public struct Vector3
    {
        public float x, y, z;
        public float magnitude;
        public float sqrMagnitude;
        public Vector3 normalized => default;

        public Vector3(float x, float y, float z) { this.x = x; this.y = y; this.z = z; magnitude = 0; sqrMagnitude = 0; }

        public static Vector3 zero => new Vector3(0, 0, 0);
        public static Vector3 one => new Vector3(1, 1, 1);
        public static Vector3 up => new Vector3(0, 1, 0);
        public static Vector3 forward => new Vector3(0, 0, 1);

        public static Vector3 operator +(Vector3 a, Vector3 b) => default;
        public static Vector3 operator -(Vector3 a, Vector3 b) => default;
        public static Vector3 operator *(Vector3 a, float d) => default;
        public static Vector3 operator *(float d, Vector3 a) => default;
    }

    public struct Quaternion
    {
        public float x, y, z, w;
        public static Quaternion identity => default;
        public static Quaternion Euler(float x, float y, float z) => default;
    }

    public struct Color
    {
        public float r, g, b, a;
        public Color(float r, float g, float b, float a = 1f) { this.r = r; this.g = g; this.b = b; this.a = a; }
        public static Color white => default;
        public static Color black => default;
        public static Color red => default;
        public static Color green => default;
        public static Color blue => default;
    }

    public struct Color32
    {
        public byte r, g, b, a;
        public Color32(byte r, byte g, byte b, byte a) { this.r = r; this.g = g; this.b = b; this.a = a; }
        public static implicit operator Color(Color32 c) => new Color(c.r / 255f, c.g / 255f, c.b / 255f, c.a / 255f);
        public static implicit operator Color32(Color c) => new Color32((byte)(c.r * 255), (byte)(c.g * 255), (byte)(c.b * 255), (byte)(c.a * 255));
    }

    public class Coroutine { }

    public class WaitForSeconds : CustomYieldInstruction
    {
        public WaitForSeconds(float seconds) { }
        public override bool keepWaiting => false;
    }

    public class WaitForFixedUpdate : CustomYieldInstruction
    {
        public override bool keepWaiting => false;
    }

    public class WaitForEndOfFrame : CustomYieldInstruction
    {
        public override bool keepWaiting => false;
    }

    public abstract class CustomYieldInstruction : System.Collections.IEnumerator
    {
        public abstract bool keepWaiting { get; }
        public object Current => null;
        public bool MoveNext() => keepWaiting;
        public void Reset() { }
    }

    public static class Time
    {
        public static float deltaTime;
        public static float fixedDeltaTime;
        public static float time;
        public static float timeScale;
    }

    public static class Input
    {
        public static float GetAxis(string axisName) => 0f;
        public static bool GetKey(string name) => false;
        public static bool GetKeyDown(string name) => false;
        public static bool GetKeyUp(string name) => false;
        public static bool GetMouseButton(int button) => false;
        public static bool GetMouseButtonDown(int button) => false;
        public static bool GetMouseButtonUp(int button) => false;
        public static Vector3 mousePosition;
    }

    public static class Debug
    {
        public static void Log(object message) { }
        public static void LogWarning(object message) { }
        public static void LogError(object message) { }
        public static void DrawLine(Vector3 start, Vector3 end, Color color = default, float duration = 0f) { }
        public static void DrawRay(Vector3 start, Vector3 dir, Color color = default, float duration = 0f) { }
    }

    public static class Mathf
    {
        public const float PI = 3.14159265f;
        public const float Infinity = float.PositiveInfinity;
        public static float Lerp(float a, float b, float t) => 0f;
        public static float Clamp(float value, float min, float max) => 0f;
        public static float Abs(float f) => 0f;
        public static float Min(float a, float b) => 0f;
        public static float Max(float a, float b) => 0f;
        public static float Sign(float f) => 0f;
        public static float Cos(float f) => 0f;
        public static float Sin(float f) => 0f;
        public static float Tan(float f) => 0f;
        public static float Acos(float f) => 0f;
        public static float Asin(float f) => 0f;
        public static float Atan(float f) => 0f;
        public static float Atan2(float y, float x) => 0f;
        public static float Sqrt(float f) => 0f;
        public static float Floor(float f) => 0f;
        public static float Ceil(float f) => 0f;
        public static float Log(float f) => 0f;
        public static float Pow(float f, float p) => 0f;
        public static float Round(float f) => 0f;
        public static float MoveTowards(float current, float target, float maxDelta) => 0f;
    }

    public static class Random
    {
        public static float value => 0f;
        public static float Range(float min, float max) => 0f;
        public static int Range(int min, int max) => 0;
    }

    public class Rigidbody2D : Component
    {
        public Vector2 velocity;
        public Vector2 linearVelocity;
        public float angularVelocity;
        public float gravityScale;
        public float mass;
        public RigidbodyType2D bodyType;

        public void AddForce(Vector2 force) { }
        public void AddForce(Vector2 force, ForceMode2D mode) { }
        public void MovePosition(Vector2 position) { }
    }

    public enum RigidbodyType2D { Dynamic, Kinematic, Static }
    public enum ForceMode2D { Force, Impulse }

    public class Collider2D : Component { }
    public class BoxCollider2D : Collider2D
    {
        public Vector2 size;
        public Vector2 offset;
        public bool isTrigger;
    }
    public class CircleCollider2D : Collider2D
    {
        public float radius;
        public Vector2 offset;
        public bool isTrigger;
    }

    public class Collision2D
    {
        public GameObject gameObject;
        public Collider2D collider;
        public Vector2 relativeVelocity;
    }

    public class SpriteRenderer : Component
    {
        public Sprite sprite;
        public Color color;
        public int sortingOrder;
        public Vector2 size;
    }

    public class Sprite : Object { }
    public class Camera : Component
    {
        public static Camera main;
        public float orthographicSize;
        public Color backgroundColor;
        public Vector3 ScreenToWorldPoint(Vector3 position) => default;
    }

    public class AudioSource : Component
    {
        public AudioClip clip;
        public float volume;
        public bool loop;
        public void Play() { }
        public void Stop() { }
        public void PlayOneShot(AudioClip clip, float volume = 1f) { }
    }

    public class AudioClip : Object { }

    // Attributes
    public class SerializeFieldAttribute : System.Attribute { }
    [System.AttributeUsage(System.AttributeTargets.Class, AllowMultiple = true)]
    public class RequireComponentAttribute : System.Attribute
    {
        public RequireComponentAttribute(System.Type type) { }
    }
    public class HeaderAttribute : System.Attribute
    {
        public HeaderAttribute(string header) { }
    }

    public enum TextAnchor
    {
        UpperLeft, UpperCenter, UpperRight,
        MiddleLeft, MiddleCenter, MiddleRight,
        LowerLeft, LowerCenter, LowerRight
    }

    public class Animator : Component
    {
        public void SetTrigger(string name) { }
        public void SetBool(string name, bool value) { }
        public void SetFloat(string name, float value) { }
        public void SetInteger(string name, int value) { }
    }

    public static class Physics2D
    {
        public static RaycastHit2D Raycast(Vector2 origin, Vector2 direction, float distance = float.PositiveInfinity) => default;
    }

    public struct RaycastHit2D
    {
        public Collider2D collider;
        public Vector2 point;
        public Vector2 normal;
        public float distance;
    }
}

namespace UnityEngine.UI
{
    public class Text : UnityEngine.Component
    {
        public string text;
        public int fontSize;
        public UnityEngine.Color color;
        public UnityEngine.TextAnchor alignment;
    }

    public class Image : UnityEngine.Component
    {
        public UnityEngine.Sprite sprite;
        public UnityEngine.Color color;
    }

    public class Button : UnityEngine.Component { }

    public class Canvas : UnityEngine.Component
    {
        public int sortOrder;
    }

    public class RectTransform : UnityEngine.Transform
    {
        public UnityEngine.Vector2 anchorMin;
        public UnityEngine.Vector2 anchorMax;
        public UnityEngine.Vector2 anchoredPosition;
        public UnityEngine.Vector2 sizeDelta;
    }
}
