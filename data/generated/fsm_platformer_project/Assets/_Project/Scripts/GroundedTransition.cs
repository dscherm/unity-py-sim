using UnityEngine;
namespace FSMPlatformer
{
    public class GroundedTransition : FSMTransition
    {
        public object player = player_input_handler;
        public bool IsValid(FSMState currentState)
        {
            return player.isGrounded;
        }
    }
}
