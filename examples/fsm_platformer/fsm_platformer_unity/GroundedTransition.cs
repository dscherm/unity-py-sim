// Unity APIs used: none (reads PlayerInputHandler state)
public class GroundedTransition : FSMTransition
{
    private PlayerInputHandler player;

    public GroundedTransition(FSMState targetState, PlayerInputHandler player) : base(targetState)
    {
        this.player = player;
    }

    public override bool IsValid(FSMState currentState)
    {
        return player.IsGrounded;
    }
}
