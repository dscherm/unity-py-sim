// Unity APIs used: none (pure C#)
public abstract class FSMTransition
{
    public FSMState TargetState { get; private set; }

    public FSMTransition(FSMState targetState)
    {
        TargetState = targetState;
    }

    public abstract bool IsValid(FSMState currentState);
}
