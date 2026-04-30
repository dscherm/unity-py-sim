using UnityEngine.InputSystem;
using UnityEngine;
namespace FSMPlatformer
{
    public class PlayerRunningState : FSMState
    {
        public void Act(MonoBehaviour owner)
        {
            PlayerInputHandler player = (PlayerInputHandler)owner;
            var direction = player.horizontalInput;
            var rb = player.rb;
            rb.linearVelocity = new Vector2(direction * player.moveSpeed, rb.linearVelocity.y);
        }
    }
}
