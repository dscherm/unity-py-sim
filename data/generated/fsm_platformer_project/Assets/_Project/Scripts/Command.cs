using UnityEngine.InputSystem;
using UnityEngine;
namespace FSMPlatformer
{
    public class Command
    {
        public PlayerInputHandler playerInputHandler = player_input_handler;
        public bool IsValid()
        {
            raise NotImplementedError;
        }
        public void DoBeforeEntering()
        {
            /* pass */
        }
        public void Act()
        {
            raise NotImplementedError;
        }
        public void DoBeforeLeaving()
        {
            /* pass */
        }
    }
    public class CommandProcessor
    {
        public Command currentCommand = null;
        public void Execute(Command? command)
        {
            if (command == null)
            {
                if (currentCommand != null)
                {
                    currentCommand.DoBeforeLeaving();
                }
                currentCommand = null;
                return;
            }
            if (!command.IsValid())
            {
                return;
            }
            if (currentCommand != null)
            {
                currentCommand.DoBeforeLeaving();
            }
            currentCommand = command;
            currentCommand.DoBeforeEntering();
        }
        public void Act()
        {
            if (currentCommand != null)
            {
                currentCommand.Act();
            }
        }
    }
}
