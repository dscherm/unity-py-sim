<!-- id: lesson-20260412-001 -->
<!-- severity: high -->
<!-- tags: unity, gamedev, unity6, scaffolder -->
<!-- applies-to: gamedev -->

# Lesson: Unity 6 Requires Explicit Audio Module in manifest.json

## Problem
Unity 6 modularized `AudioSource` into a separate built-in package
(`com.unity.modules.audio`). Generated C# code using
`GetComponent<AudioSource>()` fails with CS1069 if the Audio module
is not listed in `Packages/manifest.json`.

## Root Cause
Unity 6 (6000.x) split core engine types into opt-in modules. Unlike
Unity 2022 where AudioSource was always available, Unity 6 requires
explicit `"com.unity.modules.audio": "1.0.0"` in the manifest.

## Fix
Add `"com.unity.modules.audio": "1.0.0"` to `_REQUIRED_PACKAGES` in
`src/exporter/project_scaffolder.py`. Also check for other modularized
types: `com.unity.modules.physics2d`, `com.unity.modules.ui`, etc.

## Validation
Breakout project: 0 errors, 4 warnings (CS0472 bool-null comparison)
in Unity 6000.4.0f1 after adding the audio module.

## Related
- CS0472 warnings: translator emits `bool != null` checks for value types.
  Should strip null checks on bool/int/float fields.
