# PARITY_SCAFFOLD_PARKED
"""Parked: UnityEngine.SceneManager is intentionally NOT parity-tested.

Reason: Scene loading is environment-bound; not meaningfully testable headless.

If a future game depends on this surface, promote this file to a real
parity test by removing the PARITY_SCAFFOLD_PARKED marker and wiring up
a ParityCase. Until then, this row counts as 'parity_skipped' rather
than 'untested' in data/metrics/parity_matrix.json.
"""
