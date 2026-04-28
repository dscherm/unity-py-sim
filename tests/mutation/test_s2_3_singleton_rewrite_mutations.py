"""Mutation tests for S2-3: singleton detection and rewrite.

Each test monkeypatches a single function to its broken form, then asserts
that our contract / behavioral tests catch the breakage.  If a mutation is
NOT caught, that is a test-gap finding (not a test-pass).

Three mutations under test:
  M1 — _detect_singleton_classes always returns empty set
  M2 — rewrite_singleton_access is a no-op (returns cs_source unchanged)
  M3 — rewrite_singleton_access ignores current_classes filter (rewrites own class)
"""

from __future__ import annotations

from unittest.mock import patch


from src.translator import semantic_layer
from src.translator import project_translator
from src.translator.semantic_layer import rewrite_singleton_access


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_CONSUMER_CS = """\
public class Player : MonoBehaviour
{
    void Update()
    {
        int s = GameManager.Instance.score;
    }
}
"""

_SINGLETON_CS = """\
public class GameManager : MonoBehaviour
{
    public static GameManager Instance;

    void Awake()
    {
        GameManager.Instance = this;
    }
}
"""

_SINGLETONS = {"GameManager"}


# ===========================================================================
# M1 — _detect_singleton_classes always returns empty set
# ===========================================================================

class TestMutation1DetectAlwaysEmpty:
    """If _detect_singleton_classes is broken to always return set(), the
    semantic transform will never know about singletons, so no rewrite happens
    and consumer classes will still contain raw .Instance. references."""

    def test_mutation_caught_by_integration(self, tmp_path):
        """translate_project() on a project with a singleton consumer must emit
        [SerializeField] injection.  With the mutation, it won't."""

        # Write a minimal project
        (tmp_path / "game_manager.py").write_text(
            "class GameManager:\n"
            "    instance = None\n"
            "    def awake(self):\n"
            "        GameManager.instance = self\n"
            "        self.score = 0\n",
            encoding="utf-8",
        )
        (tmp_path / "player.py").write_text(
            "class Player:\n"
            "    def update(self):\n"
            "        s = GameManager.instance.score\n",
            encoding="utf-8",
        )

        # BASELINE — no mutation: Player.cs should have the injection
        from src.translator.project_translator import translate_project
        results_clean = translate_project(str(tmp_path))
        player_clean = results_clean.get("Player.cs", "")
        assert "[SerializeField] private GameManager gameManager;" in player_clean, (
            "Baseline broken: Player.cs has no SerializeField injection even before mutation. "
            f"Got:\n{player_clean}"
        )

        # MUTATED — _detect_singleton_classes always returns empty set
        with patch.object(
            project_translator,
            "_detect_singleton_classes",
            return_value=set(),
        ):
            results_mutated = translate_project(str(tmp_path))

        player_mutated = results_mutated.get("Player.cs", "")

        # The mutation MUST produce a different (broken) result
        assert "[SerializeField] private GameManager gameManager;" not in player_mutated, (
            "Mutation M1 not observable: detection-disabled still produced SerializeField "
            f"injection.\nGot:\n{player_mutated}"
        )

    def test_mutation_detected_no_rewrite_without_singletons(self):
        """Direct call: rewrite_singleton_access with empty singletons set must
        NOT rewrite anything — proving that detection is the gate."""
        result = rewrite_singleton_access(
            _CONSUMER_CS,
            singletons=set(),
            current_classes=set(),
        )
        # With the mutation (empty singletons), the consumer is unchanged
        assert "GameManager.Instance" in result
        assert "[SerializeField]" not in result


# ===========================================================================
# M2 — rewrite_singleton_access is a no-op
# ===========================================================================

class TestMutation2RewriteNoOp:
    """If rewrite_singleton_access simply returns the input unchanged, consumers
    retain raw .Instance. calls and do NOT get SerializeField injections."""

    def test_mutation_caught_by_consumer_check(self):
        """Verify that the real function changes the source (not a no-op)."""
        result = rewrite_singleton_access(
            _CONSUMER_CS,
            singletons=_SINGLETONS,
            current_classes=set(),
        )
        # The real function must change the source
        assert result != _CONSUMER_CS, (
            "rewrite_singleton_access is a no-op: returned source unchanged.\n"
            f"Input:\n{_CONSUMER_CS}\nOutput:\n{result}"
        )

    def test_mutation_caught_by_serializefield_check(self):
        """No-op rewriter would leave no [SerializeField]; real must inject it."""
        result = rewrite_singleton_access(
            _CONSUMER_CS,
            singletons=_SINGLETONS,
            current_classes=set(),
        )
        assert "[SerializeField] private GameManager gameManager;" in result, (
            f"rewrite_singleton_access did not inject [SerializeField].\nGot:\n{result}"
        )

    def test_mutation_caught_by_instance_removal_check(self):
        """No-op rewriter would leave .Instance. calls; real must remove them."""
        result = rewrite_singleton_access(
            _CONSUMER_CS,
            singletons=_SINGLETONS,
            current_classes=set(),
        )
        assert "GameManager.Instance" not in result, (
            f"rewrite_singleton_access left raw GameManager.Instance in output.\nGot:\n{result}"
        )

    def test_mutation_caught_via_transform(self):
        """Verify through the transform() facade that the rewrite actually fires."""
        from src.translator.semantic_layer import transform
        result = transform(
            _CONSUMER_CS,
            singletons=_SINGLETONS,
            current_classes=set(),
        )
        assert "[SerializeField] private GameManager gameManager;" in result, (
            f"transform() did not produce SerializeField injection.\nGot:\n{result}"
        )
        assert "GameManager.Instance" not in result

    def test_noop_mutation_observable_via_mock(self):
        """Explicitly apply the no-op mutation, confirm tests would catch it."""
        with patch.object(
            semantic_layer,
            "rewrite_singleton_access",
            side_effect=lambda cs, **kw: cs,  # no-op
        ):
            from src.translator.semantic_layer import transform
            # transform() calls rewrite_singleton_access internally
            result = transform(
                _CONSUMER_CS,
                singletons=_SINGLETONS,
                current_classes=set(),
            )

        # With no-op, GameManager.Instance survives
        assert "GameManager.Instance" in result, (
            "Mutation M2 not observable via mock — source was modified despite no-op patch."
        )
        # And no SerializeField was injected
        assert "[SerializeField] private GameManager gameManager;" not in result


# ===========================================================================
# M3 — current_classes filter ignored (own class gets rewritten too)
# ===========================================================================

class TestMutation3FilterIgnored:
    """If rewrite_singleton_access ignores current_classes, it will rewrite
    GameManager's own body — turning `GameManager.Instance = this;` into
    `gameManager.Instance = this;` (broken C#) and injecting a spurious
    self-reference SerializeField."""

    def test_real_function_skips_own_class(self):
        """Baseline: the real function must NOT rewrite GameManager's own body."""
        result = rewrite_singleton_access(
            _SINGLETON_CS,
            singletons=_SINGLETONS,
            current_classes={"GameManager"},
        )
        # Self-initialization must survive untouched
        assert "GameManager.Instance = this;" in result, (
            f"GameManager.Instance = this; was corrupted by rewriter.\nGot:\n{result}"
        )

    def test_real_function_no_serializefield_in_own_class(self):
        result = rewrite_singleton_access(
            _SINGLETON_CS,
            singletons=_SINGLETONS,
            current_classes={"GameManager"},
        )
        assert "[SerializeField] private GameManager gameManager;" not in result, (
            f"Rewriter injected self-reference [SerializeField] into GameManager.\nGot:\n{result}"
        )

    def test_mutation_observable_when_filter_ignored(self):
        """Simulate the mutation: pass current_classes=set() for own class.
        The broken result must differ from the correct (filtered) result."""
        # Correct result: own class is skipped
        result_correct = rewrite_singleton_access(
            _SINGLETON_CS,
            singletons=_SINGLETONS,
            current_classes={"GameManager"},
        )
        # Mutated result: filter is bypassed (simulate by passing empty current_classes)
        result_mutated = rewrite_singleton_access(
            _SINGLETON_CS,
            singletons=_SINGLETONS,
            current_classes=set(),
        )
        # The mutation must produce a different (broken) output
        assert result_correct != result_mutated, (
            "Mutation M3 not observable: filter bypass produces identical output to filtered run."
        )

    def test_mutation_corrupts_singleton_init(self):
        """With the filter disabled, the rewriter corrupts GameManager.Instance = this;."""
        result_mutated = rewrite_singleton_access(
            _SINGLETON_CS,
            singletons=_SINGLETONS,
            current_classes=set(),  # filter bypassed
        )
        # The self-initialization must now be corrupted (Instance replaced with field name)
        assert "GameManager.Instance = this;" not in result_mutated or \
               "[SerializeField] private GameManager gameManager;" in result_mutated, (
            "Mutation M3 not observable: filter bypass did not alter singleton's own body."
        )

    def test_consumer_still_rewritten_with_filter_active(self):
        """With filter correctly active, CONSUMER classes must still be rewritten.

        Real calling contract (from project_translator.py):
          current_classes = {cls.name for cls in parsed.classes}
          → for a file that defines Player, current_classes = {'Player'}
          → for a file that defines GameManager, current_classes = {'GameManager'}

        So when processing Player.cs, current_classes is {'Player'} — GameManager
        is NOT in current_classes, so it is a foreign singleton that must be rewritten.
        """
        # Realistic scenario: processing Player.cs whose only class is Player
        result = rewrite_singleton_access(
            _CONSUMER_CS,
            singletons=_SINGLETONS,
            current_classes={"Player"},  # classes defined in THIS file (Player.cs)
        )
        assert "[SerializeField] private GameManager gameManager;" in result, (
            f"Consumer class was not rewritten even though it is not in current_classes.\nGot:\n{result}"
        )
        assert "GameManager.Instance" not in result


# ===========================================================================
# M1+M2 combined: detection dead + rewrite dead — integration still catches it
# ===========================================================================

class TestCombinedMutations:
    """Verify that a test can tell when both detection AND rewrite are broken."""

    def test_combined_mutation_leaves_no_serializefield(self, tmp_path):
        (tmp_path / "game_manager.py").write_text(
            "class GameManager:\n"
            "    instance = None\n"
            "    def awake(self):\n"
            "        GameManager.instance = self\n"
            "        self.score = 0\n",
            encoding="utf-8",
        )
        (tmp_path / "player.py").write_text(
            "class Player:\n"
            "    def update(self):\n"
            "        s = GameManager.instance.score\n",
            encoding="utf-8",
        )

        from src.translator.project_translator import translate_project

        with patch.object(project_translator, "_detect_singleton_classes", return_value=set()), \
             patch.object(semantic_layer, "rewrite_singleton_access", side_effect=lambda cs, **kw: cs):
            results = translate_project(str(tmp_path))

        player_cs = results.get("Player.cs", "")
        # With both mutations, no injection should appear
        assert "[SerializeField] private GameManager gameManager;" not in player_cs
