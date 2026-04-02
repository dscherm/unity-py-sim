using UnityEngine;

// Unity APIs used: MonoBehaviour, Rigidbody2D, Vector2
public class PlayerFallingState : FSMState
{
    public override void Act(MonoBehaviour owner)
    {
        PlayerInputHandler player = (PlayerInputHandler)owner;
        float h = player.HorizontalInput;
        Rigidbody2D rb = player.Rb;
        rb.linearVelocity = new Vector2(h * player.MoveSpeed, rb.linearVelocity.y);
    }
}
