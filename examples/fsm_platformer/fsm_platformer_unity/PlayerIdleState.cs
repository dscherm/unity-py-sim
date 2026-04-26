using UnityEngine;

// Unity APIs used: MonoBehaviour, Rigidbody2D, Vector2
public class PlayerIdleState : FSMState
{
    public override void DoBeforeEntering()
    {
        base.DoBeforeEntering();
    }

    public override void Act(MonoBehaviour owner)
    {
        PlayerInputHandler player = (PlayerInputHandler)owner;
        Rigidbody2D rb = player.Rb;
        rb.linearVelocity = new Vector2(0, rb.linearVelocity.y);
    }
}
