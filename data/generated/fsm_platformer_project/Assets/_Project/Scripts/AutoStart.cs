using System.Linq;
using System.Reflection;
using UnityEngine;

// Scaffolder fixture (data/lessons/flappy_bird_deploy.md gap 1).
// Un-pauses the game at runtime when GameManager.Start() calls
// Pause() expecting a UI Play button that the generator can't wire.
public class AutoStart : MonoBehaviour
{
    void Start()
    {
        System.Type type = null;
        foreach (var asm in System.AppDomain.CurrentDomain.GetAssemblies())
        {
            try
            {
                type = asm.GetTypes().FirstOrDefault(t => t.Name == "GameManager");
            }
            catch (ReflectionTypeLoadException) { continue; }
            if (type != null) break;
        }
        if (type == null) return;
        var flags = BindingFlags.Public | BindingFlags.Static;
        var field = type.GetField("instance", flags) ?? type.GetField("Instance", flags);
        if (field == null) return;
        var gm = field.GetValue(null);
        if (gm == null) return;
        var play = type.GetMethod("Play");
        if (play != null) play.Invoke(gm, null);
    }
}
