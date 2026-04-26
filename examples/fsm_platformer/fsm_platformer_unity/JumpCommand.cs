using UnityEngine;

// Unity APIs used: MonoBehaviour, Rigidbody2D, Vector2
public class JumpCommand : Command
{
    public JumpCommand(PlayerInputHandler handler) : base(handler) { }

    public override bool IsValid()
    {
        return playerInputHandler.IsGrounded;
    }

    public override void DoBeforeEntering() { }

    public override void Act()
    {
        if (playerInputHandler.IsGrounded)
        {
            playerInputHandler.Rb.linearVelocity = new Vector2(
                playerInputHandler.Rb.linearVelocity.x,
                playerInputHandler.JumpForce);
        }
    }
}
