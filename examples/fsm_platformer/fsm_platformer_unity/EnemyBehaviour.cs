using UnityEngine;
using TMPro;

// Unity APIs used: MonoBehaviour, Rigidbody2D, SerializeField, TextMeshProUGUI
public class EnemyBehaviour : MonoBehaviour
{
    [Header("AI Settings")]
    [SerializeField] private float idleTime = 2f;
    [SerializeField] private float walkTime = 3f;
    [SerializeField] private float walkSpeed = 1.5f;

    [Header("UI")]
    [SerializeField] private TextMeshProUGUI stateText;

    private FSM fsm;
    private Rigidbody2D rb;

    public Rigidbody2D Rb => rb;

    private void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
    }

    private void Start()
    {
        fsm = new FSM();

        var idleState = new IdleState();
        var walkState = new WalkState(walkSpeed);

        idleState.AddTransition(new TimeTransition(walkState, idleTime));
        walkState.AddTransition(new TimeTransition(idleState, walkTime));

        fsm.AddState(idleState);
        fsm.AddState(walkState);
    }

    private void Update()
    {
        fsm.Update(this);

        if (stateText != null)
        {
            stateText.text = fsm.CurrentState.GetType().Name;
        }
    }
}
