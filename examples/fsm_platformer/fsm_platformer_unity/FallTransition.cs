using UnityEngine;

// Unity APIs used: Rigidbody2D.linearVelocity
public class FallTransition : FSMTransition
{
    private PlayerInputHandler player;

    public FallTransition(FSMState targetState, PlayerInputHandler player) : base(targetState)
    {
        this.player = player;
    }

    public override bool IsValid(FSMState currentState)
    {
        return player.Rb.linearVelocity.y <= 0;
    }
}
