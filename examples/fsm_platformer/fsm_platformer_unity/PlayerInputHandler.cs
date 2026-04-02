using UnityEngine;
using UnityEngine.InputSystem;

// Unity APIs used: MonoBehaviour, Rigidbody2D, Physics2D.OverlapCircle,
//   Transform, LayerMask, InputActionAsset, InputAction, Vector2, Time
public class PlayerInputHandler : MonoBehaviour
{
    [Header("Movement")]
    [SerializeField] private float moveSpeed = 3f;
    [SerializeField] private float jumpForce = 5f;

    [Header("Ground Check")]
    [SerializeField] private Transform groundCheck;
    [SerializeField] private float groundCheckRadius = 0.2f;
    [SerializeField] private LayerMask groundLayer;

    [Header("Input")]
    [SerializeField] private InputActionAsset inputActionAsset;

    private Rigidbody2D rb;
    private FSM fsm;
    private CommandProcessor commandProcessor;
    private WalkCommand walkCommand;
    private JumpCommand jumpCommand;

    // FSM states (cached for type checks)
    private PlayerIdleState idleState;
    private PlayerRunningState runningState;
    private PlayerJumpingState jumpingState;
    private PlayerFallingState fallingState;
    private PlayerLandingState landingState;

    private InputAction moveAction;
    private InputAction jumpAction;

    public Rigidbody2D Rb => rb;
    public float MoveSpeed => moveSpeed;
    public float JumpForce => jumpForce;
    public bool IsGrounded { get; private set; }
    public float HorizontalInput { get; private set; }
    public bool JumpPressed { get; private set; }
    public FSM Fsm => fsm;

    private void Awake()
    {
        rb = GetComponent<Rigidbody2D>();

        // Input System setup
        var gameplayMap = inputActionAsset.FindActionMap("Gameplay");
        moveAction = gameplayMap.FindAction("Move");
        jumpAction = gameplayMap.FindAction("Jump");
        gameplayMap.Enable();
    }

    private void Start()
    {
        // Create states
        idleState = new PlayerIdleState();
        runningState = new PlayerRunningState();
        jumpingState = new PlayerJumpingState();
        fallingState = new PlayerFallingState();
        landingState = new PlayerLandingState();

        // Wire transition table
        // IDLE: jump -> JUMPING, input -> RUNNING
        idleState.AddTransition(new JumpTransition(jumpingState, this));
        idleState.AddTransition(new InputTransition(runningState, this));

        // RUNNING: jump -> JUMPING, no input -> IDLE
        runningState.AddTransition(new JumpTransition(jumpingState, this));
        runningState.AddTransition(new NoInputTransition(idleState, this));

        // JUMPING: fall (vy <= 0) -> FALLING
        jumpingState.AddTransition(new FallTransition(fallingState, this));

        // FALLING: grounded -> LANDING
        fallingState.AddTransition(new GroundedTransition(landingState, this));

        // LANDING: timer (0.1s) -> IDLE
        landingState.AddTransition(new LandingTimerTransition(idleState));

        // Build FSM (first state = initial)
        fsm = new FSM();
        fsm.AddState(idleState);
        fsm.AddState(runningState);
        fsm.AddState(jumpingState);
        fsm.AddState(fallingState);
        fsm.AddState(landingState);

        // Commands
        walkCommand = new WalkCommand(this);
        jumpCommand = new JumpCommand(this);
        commandProcessor = new CommandProcessor();
    }

    private void Update()
    {
        // Read input via new Input System
        HorizontalInput = moveAction.ReadValue<Vector2>().x;
        JumpPressed = jumpAction.WasPressedThisFrame();

        // Ground check
        IsGrounded = Physics2D.OverlapCircle(groundCheck.position, groundCheckRadius, groundLayer);

        // Update FSM
        fsm.Update(this);

        // Gate commands by FSM state
        FSMState current = fsm.CurrentState;
        if (current is PlayerIdleState || current is PlayerRunningState)
        {
            if (HorizontalInput != 0)
            {
                commandProcessor.Execute(walkCommand);
            }
            else if (commandProcessor.CurrentCommand == walkCommand)
            {
                commandProcessor.Execute(null);
            }

            if (JumpPressed)
            {
                commandProcessor.Execute(jumpCommand);
            }
        }
        else if (current is PlayerFallingState || current is PlayerLandingState)
        {
            if (commandProcessor.CurrentCommand != null)
            {
                commandProcessor.Execute(null);
            }
        }

        // Tick command
        commandProcessor.Act();
    }

    private void OnDrawGizmosSelected()
    {
        if (groundCheck != null)
        {
            Gizmos.color = Color.red;
            Gizmos.DrawWireSphere(groundCheck.position, groundCheckRadius);
        }
    }
}
