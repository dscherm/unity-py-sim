using UnityEngine.InputSystem;
using UnityEngine;
namespace FSMPlatformer
{
    public class PlayerJumpingState : FSMState
    {
        public void DoBeforeEntering()
        {
            base.DoBeforeEntering();
        }
        public void Act(MonoBehaviour owner)
        {
            PlayerInputHandler player = (PlayerInputHandler)owner;
            var rb = player.rb;
            var h = player.horizontalInput;
            rb.linearVelocity = new Vector2(h * player.moveSpeed, rb.linearVelocity.y);
        }
    }
}
