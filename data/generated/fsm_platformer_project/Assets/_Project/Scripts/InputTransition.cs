using UnityEngine;
namespace FSMPlatformer
{
    public class InputTransition : FSMTransition
    {
        public object player = player_input_handler;
        public bool IsValid(FSMState currentState)
        {
            return player.horizontalInput != 0;
        }
    }
}
