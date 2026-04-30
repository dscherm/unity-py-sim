using UnityEngine;
namespace FSMPlatformer
{
    public class JumpCommand : Command
    {
        public bool IsValid()
        {
            return playerInputHandler.isGrounded;
        }
        public void DoBeforeEntering()
        {
            /* pass */
        }
        public void Act()
        {
            var player = playerInputHandler;
            if (player.isGrounded)
            {
                var rb = player.rb;
                rb.linearVelocity = new Vector2(rb.linearVelocity.x, player.jumpForce);
            }
        }
    }
}
