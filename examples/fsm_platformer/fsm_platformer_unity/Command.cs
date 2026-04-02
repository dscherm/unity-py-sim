// Unity APIs used: none (pure C#)
public abstract class Command
{
    protected PlayerInputHandler playerInputHandler;

    public Command(PlayerInputHandler handler)
    {
        playerInputHandler = handler;
    }

    public abstract bool IsValid();
    public abstract void Act();
    public virtual void DoBeforeEntering() { }
    public virtual void DoBeforeLeaving() { }
}
