using UnityEngine;
namespace FSMPlatformer
{
    public class WalkCommand : Command
    {
        public bool IsValid()
        {
            return true;
        }
        public void DoBeforeEntering()
        {
            var h = playerInputHandler.horizontalInput;
            var scale = playerInputHandler.transform.localScale;
            if ((h > 0 && scale.x < 0) || (h < 0 && scale.x > 0))
            {
                playerInputHandler.transform.localScale = new Vector3( -scale.x, scale.y, scale.z );
            }
        }
        public void Act()
        {
            var player = playerInputHandler;
            var direction = player.transform.localScale.x > 0 ? 1.0f : -1.0f;
            var rb = player.rb;
            rb.linearVelocity = new Vector2(direction * player.moveSpeed, rb.linearVelocity.y);
        }
        public void DoBeforeLeaving()
        {
            var rb = playerInputHandler.rb;
            rb.linearVelocity = new Vector2(0, rb.linearVelocity.y);
        }
    }
}
