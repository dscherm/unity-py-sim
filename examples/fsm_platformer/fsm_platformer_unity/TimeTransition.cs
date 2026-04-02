// Unity APIs used: none (reads FSMState.TimeState)
public class TimeTransition : FSMTransition
{
    private float totalTime;

    public TimeTransition(FSMState targetState, float duration) : base(targetState)
    {
        totalTime = duration;
    }

    public override bool IsValid(FSMState currentState)
    {
        return currentState.TimeState >= totalTime;
    }
}
