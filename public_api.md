# Public API

This file is the single source of shape information that the blind-TDD
test writer can read. It MUST stay in sync with `src/` — any commit that
adds, removes, or renames a public function must update this file in the
same commit. Keep it tight: names, signatures, return types, and the
minimum semantic notes a test author needs. No implementation details.

---

## `src.engine.math.mathf.Mathf`

Static utility class mirroring UnityEngine.Mathf. All methods are
`@staticmethod`. Angles are measured in **degrees** unless the method
name says otherwise (e.g. trig functions use radians, matching Unity).

### Currently implemented

- `clamp(value: float, min_val: float, max_val: float) -> float`
- `clamp01(value: float) -> float`
- `lerp(a: float, b: float, t: float) -> float` — `t` clamped to [0, 1]
- `lerp_unclamped(a: float, b: float, t: float) -> float`
- `inverse_lerp(a: float, b: float, value: float) -> float`
- `move_towards(current: float, target: float, max_delta: float) -> float`
- `approximately(a: float, b: float) -> bool`
- `smooth_step(from_: float, to: float, t: float) -> float`
- `repeat(t: float, length: float) -> float`
- `ping_pong(t: float, length: float) -> float`
- `sign(f: float) -> float` — returns -1, 0, or 1
- `abs(f: float) -> float`
- `floor(f: float) -> int`
- `ceil(f: float) -> int`
- `round(f: float) -> int`
- `min(a: float, b: float) -> float`
- `max(a: float, b: float) -> float`
- `sqrt(f: float) -> float`
- `pow(f: float, p: float) -> float`
- `sin(f: float) -> float` — radians, matches Unity
- `cos(f: float) -> float` — radians, matches Unity
- `atan2(y: float, x: float) -> float` — radians, matches Unity

### Pending (introduced by current task)

- `delta_angle(current: float, target: float) -> float` — **not yet implemented**.
  Returns the shortest signed angular difference between two angles in
  degrees. Result is in the half-open range `(-180, 180]`. Wraps around
  the 360° boundary so `delta_angle(350, 10) == 20` and
  `delta_angle(10, 350) == -20`. Matches `UnityEngine.Mathf.DeltaAngle`.

### Module

```python
from src.engine.math.mathf import Mathf
# or
from src.engine.math import Mathf  # re-exported at package level
```

---

## Notes for test authors

- Tests that exercise `Mathf` static methods should NOT instantiate
  `Mathf` — call methods directly on the class.
- Floating-point comparisons should use a tolerance of `1e-4` or
  `Mathf.approximately(a, b)`. Do not use exact `==` on float results.
- Angles at the boundary (180°, -180°) are a sharp edge — Unity returns
  `180` (positive) for `DeltaAngle(0, 180)` and `-180` is not produced.
  Test the boundary behavior explicitly.
