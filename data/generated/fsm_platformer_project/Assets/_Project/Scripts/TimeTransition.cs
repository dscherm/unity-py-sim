using UnityEngine;
namespace FSMPlatformer
{
    public class TimeTransition : FSMTransition
    {
        public float duration = duration;
        public bool IsValid(FSMState currentState)
        {
            return currentState.timeState >= duration;
        }
    }
}
