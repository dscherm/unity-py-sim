# PARITY_SCAFFOLD_PARKED
"""Parked: UnityEngine.Camera.backgroundColor is deferred (NOT out-of-scope).

Reason: Same RGB-tuple-vs-Color-struct normalization gap as
SpriteRenderer.color — Python sim stores the value as a tuple; Unity exposes
it as a Color struct. The behavior is in-scope for the simulator long-term,
just deferred until the stub work lands. Tracked in SUCCESS.md ASP-3.

If a future game depends on this surface, promote this file to a real parity
test by removing the PARITY_SCAFFOLD_PARKED marker and wiring up a ParityCase
with the Color-struct round-trip. Until then, this row counts as
'parity_skipped' rather than 'untested' in data/metrics/parity_matrix.json.
"""
