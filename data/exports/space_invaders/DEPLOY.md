# Space Invaders — Unity Deployment Guide

Generated from py-unity-sim Python simulation via the translation pipeline.

## Pipeline Results

| Step | Status |
|------|--------|
| Python → C# Translation | 7 files generated |
| Post-processing (docstrings, imports) | 6/7 syntax clean |
| Scene Serialization | 12 GameObjects, 43 components |
| CoPlay Editor Script | 276 lines |
| Translation Score | 86.1% (target 85%) |

## Files to Deploy

### 1. C# Scripts → `Assets/Scripts/`
Copy from `cleaned_cs/`:
- Player.cs, Projectile.cs, Invader.cs, Invaders.cs
- Bunker.cs, MysteryShip.cs, GameManager.cs

### 2. Assets → Copy from reference repo
Source: `D:/Projects/space-invaders-ref/Assets/`
- `Sprites/` → `Assets/Sprites/` (12 PNG files)
- `Prefabs/` → `Assets/Prefabs/` (6 prefab files)

### 3. Scene Setup
Option A: Use CoPlay MCP `execute_script` with `SceneSetup.cs`
Option B: Open reference scene from `Assets/Scenes/Space Invaders.unity`

### 4. Layer Setup (required)
Create these layers in Unity (Edit → Project Settings → Tags and Layers):
- Layer 8: Laser
- Layer 9: Missile
- Layer 10: Invader
- Layer 11: Boundary

### Manual Fixes Needed
1. `GameManager.cs` line ~238: Remove `except Exception:;` (try/catch artifact)
2. Field naming: Some generated fields use `_invokeTimer` instead of `invokeTimer`
3. Layer constants: Replace numeric `LAYER_LASER = 8` with `LayerMask.NameToLayer("Laser")`
4. `Instantiate` calls: Replace inline GameObject creation with prefab references
