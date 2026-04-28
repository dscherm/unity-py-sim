# PARITY_SCAFFOLD_PARKED
"""Parked: UnityEngine.SpriteRenderer.color is deferred (NOT out-of-scope).

Reason: Faithful parity needs RGB-tuple-vs-Color-struct normalization in the
stub layer (Python sim stores `color` as a 3-/4-tuple; Unity exposes a Color
struct). The behavior is in-scope for the simulator long-term, just deferred
until the stub work lands. Tracked in SUCCESS.md ASP-3 ("Remaining 7 untested
APIs are explicitly deferred").

If a future game depends on this surface, promote this file to a real parity
test by removing the PARITY_SCAFFOLD_PARKED marker and wiring up a ParityCase
with the Color-struct round-trip. Until then, this row counts as
'parity_skipped' rather than 'untested' in data/metrics/parity_matrix.json.
"""
