using System.Collections.Generic;
using UnityEngine.InputSystem;
using UnityEngine;
namespace FSMPlatformer
{
    public class FSMState
    {
        public FSMTransition[] transitions = null;
        public float timeState = 0.0f;
        public void AddTransition(FSMTransition transition)
        {
            transitions.Add(transition);
        }
        public FSMState CheckTransitions()
        {
            foreach (var t in transitions)
            {
                if (t.IsValid(this))
                {
                    return t.targetState;
                }
            }
            return null;
        }
        public void DoBeforeEntering()
        {
            timeState = 0.0f;
        }
        public void DoBeforeLeaving()
        {
            /* pass */
        }
        public void Act(MonoBehaviour owner)
        {
            raise NotImplementedError;
        }
    }
    public class FSMTransition
    {
        public FSMState targetState = target_state;
        public bool IsValid(FSMState currentState)
        {
            raise NotImplementedError;
        }
    }
    public class FSM
    {
        public FSMState[] states = null;
        public FSMState currentState = null;
        public void AddState(FSMState state)
        {
            states.Add(state);
            if (currentState == null)
            {
                currentState = state;
                currentState.DoBeforeEntering();
            }
        }
         void Update(MonoBehaviour owner)
        {
            if (currentState == null)
            {
                return;
            }
            currentState.timeState += Time.deltaTime;
            var nextState = currentState.CheckTransitions();
            if (nextState != null)
            {
                currentState.DoBeforeLeaving();
                currentState = nextState;
                currentState.DoBeforeEntering();
            }
            currentState.Act(owner);
        }
    }
}
