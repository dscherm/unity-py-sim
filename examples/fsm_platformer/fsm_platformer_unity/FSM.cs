using System.Collections.Generic;
using UnityEngine;

// Unity APIs used: MonoBehaviour, Time.deltaTime
public class FSM
{
    private List<FSMState> states = new List<FSMState>();
    private FSMState currentState;

    public FSMState CurrentState => currentState;

    public void AddState(FSMState state)
    {
        states.Add(state);
        if (currentState == null)
        {
            currentState = state;
            currentState.DoBeforeEntering();
        }
    }

    /// <summary>
    /// Tick the FSM. Takes MonoBehaviour so it works for both Player and Enemy.
    /// </summary>
    public void Update(MonoBehaviour owner)
    {
        if (currentState == null) return;

        currentState.TimeState += Time.deltaTime;

        FSMState nextState = currentState.CheckTransitions();
        if (nextState != null)
        {
            currentState.DoBeforeLeaving();
            currentState = nextState;
            currentState.DoBeforeEntering();
        }

        currentState.Act(owner);
    }
}
