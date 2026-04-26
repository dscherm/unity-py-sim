using System.Collections.Generic;
using UnityEngine;

// Unity APIs used: MonoBehaviour, Time.deltaTime
public abstract class FSMState
{
    protected List<FSMTransition> transitions = new List<FSMTransition>();
    public float TimeState { get; set; }

    public void AddTransition(FSMTransition transition)
    {
        transitions.Add(transition);
    }

    public FSMState CheckTransitions()
    {
        foreach (var t in transitions)
        {
            if (t.IsValid(this))
                return t.TargetState;
        }
        return null;
    }

    public virtual void DoBeforeEntering() { TimeState = 0f; }
    public virtual void DoBeforeLeaving() { }

    /// <summary>
    /// Execute per-frame logic. Takes MonoBehaviour (not EnemyBehaviour) so the
    /// FSM works for both Player and Enemy controllers.
    /// </summary>
    public abstract void Act(MonoBehaviour owner);
}
