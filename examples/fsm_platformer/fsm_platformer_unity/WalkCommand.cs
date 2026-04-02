using UnityEngine;
using UnityEngine.InputSystem;

// Unity APIs used: MonoBehaviour, Rigidbody2D, Vector2, Vector3, Transform, InputAction
public class WalkCommand : Command
{
    public WalkCommand(PlayerInputHandler handler) : base(handler) { }

    public override bool IsValid()
    {
        return true;
    }

    public override void DoBeforeEntering()
    {
        float input = playerInputHandler.HorizontalInput;
        float currentScale = playerInputHandler.transform.localScale.x;

        // Flip sprite to face movement direction
        if ((input > 0 && currentScale < 0) || (input < 0 && currentScale > 0))
        {
            Vector3 scale = playerInputHandler.transform.localScale;
            scale.x *= -1;
            playerInputHandler.transform.localScale = scale;
        }
    }

    public override void Act()
    {
        float moveSpeed = playerInputHandler.MoveSpeed;
        float dir = playerInputHandler.transform.localScale.x > 0 ? 1f : -1f;
        playerInputHandler.Rb.linearVelocity = new Vector2(
            dir * moveSpeed, playerInputHandler.Rb.linearVelocity.y);
    }

    public override void DoBeforeLeaving()
    {
        playerInputHandler.Rb.linearVelocity = new Vector2(
            0, playerInputHandler.Rb.linearVelocity.y);
    }
}
