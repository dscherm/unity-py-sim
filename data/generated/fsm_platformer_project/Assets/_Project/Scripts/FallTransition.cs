using UnityEngine;
namespace FSMPlatformer
{
    public class FallTransition : FSMTransition
    {
        public object player = player_input_handler;
        public bool IsValid(FSMState currentState)
        {
            return player.rb.linearVelocity.y <= 0;
        }
    }
}
