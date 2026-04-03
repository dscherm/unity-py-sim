// Minimal UnityEngine.InputSystem stubs for compilation gate.

namespace UnityEngine.InputSystem
{
    public class InputDevice { }

    public class Mouse : InputDevice
    {
        public static Mouse current;
        public ButtonControl leftButton;
        public ButtonControl rightButton;
        public ButtonControl middleButton;
        public Vector2Control position;
    }

    public class Keyboard : InputDevice
    {
        public static Keyboard current;
        public KeyControl spaceKey, escapeKey, enterKey, tabKey;
        public KeyControl leftArrowKey, rightArrowKey, upArrowKey, downArrowKey;
        public KeyControl leftShiftKey, rightShiftKey, leftCtrlKey, rightCtrlKey;
        public KeyControl aKey, bKey, cKey, dKey, eKey, fKey, gKey, hKey;
        public KeyControl iKey, jKey, kKey, lKey, mKey, nKey, oKey, pKey;
        public KeyControl qKey, rKey, sKey, tKey, uKey, vKey, wKey, xKey;
        public KeyControl yKey, zKey;
    }

    public class InputControl<T>
    {
        public T ReadValue() => default;
    }

    public class ButtonControl : InputControl<float>
    {
        public bool isPressed;
        public bool wasPressedThisFrame;
        public bool wasReleasedThisFrame;
    }

    public class KeyControl : ButtonControl { }

    public class Vector2Control : InputControl<UnityEngine.Vector2> { }
}
