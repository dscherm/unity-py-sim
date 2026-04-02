using UnityEngine;

// Unity APIs used: MonoBehaviour, Rigidbody2D, Vector2
public class IdleState : FSMState
{
    public override void DoBeforeEntering()
    {
        base.DoBeforeEntering();
    }

    public override void Act(MonoBehaviour owner)
    {
        EnemyBehaviour enemy = (EnemyBehaviour)owner;
        enemy.Rb.linearVelocity = new Vector2(0, enemy.Rb.linearVelocity.y);
    }
}
