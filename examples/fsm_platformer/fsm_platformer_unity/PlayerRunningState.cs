using UnityEngine;

// Unity APIs used: MonoBehaviour, Rigidbody2D, Vector2
public class PlayerRunningState : FSMState
{
    public override void Act(MonoBehaviour owner)
    {
        PlayerInputHandler player = (PlayerInputHandler)owner;
        float direction = player.HorizontalInput;
        Rigidbody2D rb = player.Rb;
        rb.linearVelocity = new Vector2(direction * player.MoveSpeed, rb.linearVelocity.y);
    }
}
