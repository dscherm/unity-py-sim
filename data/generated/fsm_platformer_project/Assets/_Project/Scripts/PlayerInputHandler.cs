using UnityEngine.InputSystem;
using UnityEngine;
namespace FSMPlatformer
{
    [RequireComponent(typeof(Rigidbody2D))]
    public class PlayerInputHandler : MonoBehaviour
    {
        public float moveSpeed = 3.0f;
        public float jumpForce = 5.0f;
        public float horizontalInput = 0.0f;
        public bool jumpPressed = false;
        public bool isGrounded = false;
        public float groundY = -3.0f;
        public Rigidbody2D rb;
        public FSM fsm;
        [SerializeField] private CommandProcessor commandProcessor;
        [SerializeField] private WalkCommand walkCommand;
        [SerializeField] private JumpCommand jumpCommand;
        public static float GROUND_CHECK_THRESHOLD = 0.15f;
         void Start()
        {
            rb = GetComponent<Rigidbody2D>();
            var idleState = new PlayerIdleState();
            var runningState = new PlayerRunningState();
            var jumpingState = new PlayerJumpingState();
            var fallingState = new PlayerFallingState();
            var landingState = new PlayerLandingState();
            idleState.AddTransition(new JumpTransition(jumpingState, this));
            idleState.AddTransition(new InputTransition(runningState, this));
            runningState.AddTransition(new JumpTransition(jumpingState, this));
            runningState.AddTransition(new NoInputTransition(idleState, this));
            jumpingState.AddTransition(new FallTransition(fallingState, this));
            fallingState.AddTransition(new GroundedTransition(landingState, this));
            landingState.AddTransition(new LandingTimerTransition(idleState));
            fsm = new FSM();
            fsm.AddState(idleState);
            fsm.AddState(runningState);
            fsm.AddState(jumpingState);
            fsm.AddState(fallingState);
            fsm.AddState(landingState);
            walkCommand = new WalkCommand(this);
            jumpCommand = new JumpCommand(this);
            commandProcessor = new CommandProcessor();
        }
         void Update()
        {
            horizontalInput = ((Keyboard.current?.dKey.isPressed == true ? 1f : 0f) - (Keyboard.current?.aKey.isPressed == true ? 1f : 0f));
            jumpPressed = Keyboard.current?.spaceKey.wasPressedThisFrame == true;
            var playerY = transform.position.y;
            var playerBottom = playerY - 0.5f;
            isGrounded = playerBottom <= groundY + GROUND_CHECK_THRESHOLD;
            fsm.Update(this);
            var current = fsm.currentState;
            if ((current is PlayerIdleState || current is PlayerRunningState))
            {
                // Allow walk and jump commands on ground
                if (horizontalInput != 0)
                {
                    commandProcessor.Execute(walkCommand);
                }
                else if (commandProcessor.currentCommand == walkCommand)
                {
                    commandProcessor.Execute(null);
                }
                if (jumpPressed)
                {
                    commandProcessor.Execute(jumpCommand);
                }
            }
            else if (current is PlayerJumpingState)
            {
                // Jump command applies force on first frame, then let physics handle it
                /* pass */
            }
            else if (current is PlayerFallingState)
            {
                // No commands while falling — FSM states handle air control
                if (commandProcessor.currentCommand != null)
                {
                    commandProcessor.Execute(null);
                }
            }
            else if (current is PlayerLandingState)
            {
                // No commands during landing
                if (commandProcessor.currentCommand != null)
                {
                    commandProcessor.Execute(null);
                }
            }
            commandProcessor.Act();
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
