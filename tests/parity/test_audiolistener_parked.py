# PARITY_SCAFFOLD_PARKED
"""Parked: UnityEngine.AudioListener is intentionally NOT parity-tested.

Reason: Audio capture; depends on AudioSource which is parked.

If a future game depends on this surface, promote this file to a real
parity test by removing the PARITY_SCAFFOLD_PARKED marker and wiring up
a ParityCase. Until then, this row counts as 'parity_skipped' rather
than 'untested' in data/metrics/parity_matrix.json.
"""
