using UnityEngine;
namespace FSMPlatformer
{
    public class EnemyIdleState : FSMState
    {
        public void Act(MonoBehaviour owner)
        {
            EnemyBehaviour enemy = (EnemyBehaviour)owner;
            var rb = enemy.rb;
            rb.linearVelocity = new Vector2(0, rb.linearVelocity.y);
        }
    }
}
