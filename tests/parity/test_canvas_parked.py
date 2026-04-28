# PARITY_SCAFFOLD_PARKED
"""Parked: UnityEngine.Canvas is intentionally NOT parity-tested.

Reason: UI rendering tree depends on Unity Editor's UI system.

If a future game depends on this surface, promote this file to a real
parity test by removing the PARITY_SCAFFOLD_PARKED marker and wiring up
a ParityCase. Until then, this row counts as 'parity_skipped' rather
than 'untested' in data/metrics/parity_matrix.json.
"""
