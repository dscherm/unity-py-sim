using UnityEngine;

// Unity APIs used: MonoBehaviour, Rigidbody2D, Vector2, Transform
public class WalkState : FSMState
{
    private float walkSpeed;

    public WalkState(float speed)
    {
        walkSpeed = speed;
    }

    public override void DoBeforeEntering()
    {
        base.DoBeforeEntering();
    }

    public override void Act(MonoBehaviour owner)
    {
        EnemyBehaviour enemy = (EnemyBehaviour)owner;
        float dir = enemy.transform.localScale.x > 0 ? -1f : 1f;
        enemy.Rb.linearVelocity = new Vector2(dir * walkSpeed, enemy.Rb.linearVelocity.y);
    }
}
