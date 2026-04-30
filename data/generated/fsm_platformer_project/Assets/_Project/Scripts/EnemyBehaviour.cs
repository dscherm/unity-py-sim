using UnityEngine;
namespace FSMPlatformer
{
    [RequireComponent(typeof(Rigidbody2D))]
    public class EnemyBehaviour : MonoBehaviour
    {
        public float idleTime = 2.0f;
        public float walkTime = 3.0f;
        public float walkSpeed = 1.5f;
        public float patrolMinX = -6.0f;
        public float patrolMaxX = 6.0f;
        public Rigidbody2D rb;
        public FSM fsm;
         void Start()
        {
            rb = GetComponent<Rigidbody2D>();
            var idleState = new EnemyIdleState();
            var walkState = new EnemyWalkState(walkSpeed);
            idleState.AddTransition(new TimeTransition(walkState, idleTime));
            walkState.AddTransition(new TimeTransition(idleState, walkTime));
            fsm = new FSM();
            fsm.AddState(idleState);
            fsm.AddState(walkState);
        }
         void Update()
        {
            fsm.Update(this);
        }
        public string StateName()
        {
            if (fsm != null && fsm.currentState != null)
            {
                return fsm.currentState.GetType().Name;
            }
            return "null";
        }
    }
}
