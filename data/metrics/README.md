# Translation Metrics Baseline

Forward-translation scoring: Python -> C# via translator, compared to hand-written C# reference.

## Summary (2026-04-03)

| Metric | Score |
|--------|-------|
| Total pairs | 37 |
| Avg overall | 0.771 |
| Avg class match | 0.860 |
| Avg method match | 0.757 |
| Avg field match | 0.709 |
| Avg using match | 0.705 |

## By Game

| Game | Pairs | Avg Overall |
|------|-------|-------------|
| pong | 4 | 0.815 |
| breakout | 5 | 0.896 |
| angry_birds | 8 | 0.763 |
| fsm_platformer | 20 | 0.734 |

## 5 Worst Pairs

1. **033_player_input_handler** (fsm, 0.273) — Python file is a monolith that builds FSM inline; C# splits across many types. Translator generates 1 class, reference has ~18.
2. **037_enemy_behaviour** (fsm, 0.407) — Same pattern: Python creates FSM/states inline, C# separates into EnemyBehaviour + state classes.
3. **036_time_transition** (fsm, 0.475) — Constructor-based class; Python __init__ pattern doesn't fully round-trip to C# constructor syntax.
4. **018_fsm** (fsm, 0.500) — FSM base class uses properties (CurrentState) that translator emits as fields.
5. **013_slingshot** (angry_birds, 0.512) — Class name mismatch (Slingshot vs SlingShot), PascalCase public fields in C# vs snake_case private fields in Python.

## Scoring Method

- **Class score** (30%): Jaccard similarity of class/enum names
- **Method score** (35%): Recall of reference method names in generated output
- **Field score** (25%): Recall of reference field names in generated output
- **Using score** (10%): Jaccard similarity of using directives

Tool: `python tools/score_baseline.py`
