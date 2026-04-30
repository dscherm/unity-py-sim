using UnityEngine;
namespace FSMPlatformer
{
    public class LandingTimerTransition : FSMTransition
    {
    private const float LANDING_DURATION = 0.1f;
        public bool IsValid(FSMState currentState)
        {
            return currentState.timeState >= LANDING_DURATION;
        }
    }
}
