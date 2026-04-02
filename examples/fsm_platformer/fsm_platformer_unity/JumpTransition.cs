// Unity APIs used: none (reads PlayerInputHandler state)
public class JumpTransition : FSMTransition
{
    private PlayerInputHandler player;

    public JumpTransition(FSMState targetState, PlayerInputHandler player) : base(targetState)
    {
        this.player = player;
    }

    public override bool IsValid(FSMState currentState)
    {
        return player.JumpPressed && player.IsGrounded;
    }
}
