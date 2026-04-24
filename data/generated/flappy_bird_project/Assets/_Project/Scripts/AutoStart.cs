using System.Reflection;
using UnityEngine;

// Scaffolder fixture (data/lessons/flappy_bird_deploy.md gap 1).
// Un-pauses the game at runtime when GameManager.Start() calls
// Pause() expecting a UI Play button that the generator can't wire.
public class AutoStart : MonoBehaviour
{
    // Run in Update, not Start — Unity's Start order is alphabetical when
    // not overridden, so AutoStart.Start runs *before* GameManager.Start
    // which then re-pauses via Time.timeScale = 0. Running in Update means
    // we fire after every Start has settled, un-pause once, and self-disable.
    bool _done;
    void Update()
    {
        if (_done) return;
        var type = System.Type.GetType("GameManager");
        if (type == null) return;
        var flags = BindingFlags.Public | BindingFlags.Static;
        var field = type.GetField("instance", flags) ?? type.GetField("Instance", flags);
        if (field == null) return;
        var gm = field.GetValue(null);
        if (gm == null) return;
        var play = type.GetMethod("Play");
        if (play != null) play.Invoke(gm, null);
        _done = true;
    }
}
