using UnityEngine.InputSystem;
using UnityEngine;
namespace FSMPlatformer
{
    public class PlayerLandingState : FSMState
    {
        public void DoBeforeEntering()
        {
            base.DoBeforeEntering();
        }
        public void Act(MonoBehaviour owner)
        {
            PlayerInputHandler player = (PlayerInputHandler)owner;
            var rb = player.rb;
            rb.linearVelocity = new Vector2(0, rb.linearVelocity.y);
        }
    }
}
