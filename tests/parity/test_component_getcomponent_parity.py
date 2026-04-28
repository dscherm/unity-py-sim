# PARITY_SCAFFOLD_PARKED
"""Parked: UnityEngine.Component.GetComponent is deferred (NOT out-of-scope).

Reason: Faithful parity needs a real component registry on the C# stub side
that lets `GetComponent<T>()` resolve sibling components by type, matching
Unity's runtime behavior. The Python sim already has this surface; the stub
layer doesn't. The behavior is in-scope long-term, just deferred until the
stub registry lands. Tracked in SUCCESS.md ASP-3.

If a future game depends on this surface, promote this file to a real parity
test by removing the PARITY_SCAFFOLD_PARKED marker and wiring up a ParityCase
that exercises sibling-component lookup. Until then, this row counts as
'parity_skipped' rather than 'untested' in data/metrics/parity_matrix.json.
"""
