// Unity APIs used: none (pure C#)
public class CommandProcessor
{
    public Command CurrentCommand { get; private set; }

    public void Execute(Command command)
    {
        if (command == null)
        {
            if (CurrentCommand != null)
                CurrentCommand.DoBeforeLeaving();
            CurrentCommand = null;
            return;
        }

        if (!command.IsValid()) return;

        if (CurrentCommand != null)
            CurrentCommand.DoBeforeLeaving();

        CurrentCommand = command;
        CurrentCommand.DoBeforeEntering();
    }

    public void Act()
    {
        CurrentCommand?.Act();
    }
}
