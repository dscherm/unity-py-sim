// Unity APIs used: none (reads PlayerInputHandler state)
public class InputTransition : FSMTransition
{
    private PlayerInputHandler player;

    public InputTransition(FSMState targetState, PlayerInputHandler player) : base(targetState)
    {
        this.player = player;
    }

    public override bool IsValid(FSMState currentState)
    {
        return player.HorizontalInput != 0;
    }
}
