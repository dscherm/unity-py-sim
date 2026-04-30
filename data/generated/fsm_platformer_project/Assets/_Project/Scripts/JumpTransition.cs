using UnityEngine;
namespace FSMPlatformer
{
    public class JumpTransition : FSMTransition
    {
        public object player = player_input_handler;
        public bool IsValid(FSMState currentState)
        {
            return player.jumpPressed && player.isGrounded;
        }
    }
}
