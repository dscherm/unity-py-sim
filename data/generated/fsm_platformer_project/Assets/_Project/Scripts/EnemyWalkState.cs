using UnityEngine;
namespace FSMPlatformer
{
    public class EnemyWalkState : FSMState
    {
        public float walkSpeed = walk_speed;
        public void Act(MonoBehaviour owner)
        {
            EnemyBehaviour enemy = (EnemyBehaviour)owner;
            var scale = enemy.transform.localScale;
            var direction = scale.x > 0 ? -1.0f : 1.0f;
            var rb = enemy.rb;
            rb.linearVelocity = new Vector2(direction * walkSpeed, rb.linearVelocity.y);
            var x = enemy.transform.position.x;
            if (x < enemy.patrolMinX)
            {
                enemy.transform.localScale = new Vector3(-Mathf.Abs(scale.x), scale.y, scale.z);
            }
            else if (x > enemy.patrolMaxX)
            {
                enemy.transform.localScale = new Vector3(Mathf.Abs(scale.x), scale.y, scale.z);
            }
        }
    }
}
