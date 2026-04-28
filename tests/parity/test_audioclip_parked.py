# PARITY_SCAFFOLD_PARKED
"""Parked: UnityEngine.AudioClip is intentionally NOT parity-tested.

Reason: Audio data type, only meaningful when AudioSource plays it.

If a future game depends on this surface, promote this file to a real
parity test by removing the PARITY_SCAFFOLD_PARKED marker and wiring up
a ParityCase. Until then, this row counts as 'parity_skipped' rather
than 'untested' in data/metrics/parity_matrix.json.
"""
