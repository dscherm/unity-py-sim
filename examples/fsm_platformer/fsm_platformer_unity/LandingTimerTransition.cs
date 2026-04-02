// Unity APIs used: none (reads FSMState.TimeState)
public class LandingTimerTransition : FSMTransition
{
    private const float LandingDuration = 0.1f;

    public LandingTimerTransition(FSMState targetState) : base(targetState) { }

    public override bool IsValid(FSMState currentState)
    {
        return currentState.TimeState >= LandingDuration;
    }
}
