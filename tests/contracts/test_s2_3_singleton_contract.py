"""Contract tests for S2-3: rewrite_singleton_access public API.

Derives expected behavior from the Unity singleton pattern specification,
not from reading the implementation.

Unity context:
- Singletons expose a static `Instance` property (PascalCase).
- Dependent MonoBehaviours must NOT hard-reference the singleton via
  `ClassName.Instance` at runtime because it couples scene load order.
- The idiomatic Unity fix: expose a `[SerializeField] private T t;` field,
  wire it in the Inspector, and reference `t.Member` instead.
"""

from __future__ import annotations

import re

import pytest

from src.translator.semantic_layer import rewrite_singleton_access


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MINIMAL_CONSUMER = """\
public class PlayerController : MonoBehaviour
{{
    void Update()
    {{
        int s = {ref}.score;
    }}
}}
"""


def _consumer(ref: str = "GameManager.Instance") -> str:
    return _MINIMAL_CONSUMER.format(ref=ref)


# ===========================================================================
# 1. Signature contract
# ===========================================================================

class TestSignature:
    """rewrite_singleton_access must accept keyword-only singletons and
    current_classes arguments (per public_api.md / task spec)."""

    def test_accepts_keyword_only_singletons(self):
        result = rewrite_singleton_access(
            _consumer(),
            singletons={"GameManager"},
            current_classes=set(),
        )
        assert isinstance(result, str)

    def test_returns_string(self):
        result = rewrite_singleton_access(
            "",
            singletons=set(),
            current_classes=set(),
        )
        assert result == ""

    def test_singletons_positional_raises(self):
        """singletons must be keyword-only; positional call must fail."""
        with pytest.raises(TypeError):
            rewrite_singleton_access(_consumer(), {"GameManager"}, set())  # type: ignore[call-arg]


# ===========================================================================
# 2. Empty-singletons contract
# ===========================================================================

class TestEmptySingletons:
    """When singletons set is empty, the source must be returned unchanged."""

    def test_no_changes_when_singletons_empty(self):
        source = _consumer("GameManager.Instance")
        result = rewrite_singleton_access(
            source,
            singletons=set(),
            current_classes=set(),
        )
        assert result == source

    def test_no_injection_when_singletons_empty(self):
        source = _consumer("GameManager.Instance")
        result = rewrite_singleton_access(
            source,
            singletons=set(),
            current_classes=set(),
        )
        assert "[SerializeField]" not in result


# ===========================================================================
# 3. Cross-class rewrite contract
# ===========================================================================

class TestCrossClassRewrite:
    """When a singleton is referenced in a class OTHER than the singleton's
    own class, the rewriter must:
      a. Inject [SerializeField] private T tCamel; into that class.
      b. Replace T.Instance with tCamel in that class body.
    """

    def test_injects_serializefield(self):
        source = _consumer("GameManager.Instance")
        result = rewrite_singleton_access(
            source,
            singletons={"GameManager"},
            current_classes=set(),
        )
        assert "[SerializeField] private GameManager gameManager;" in result

    def test_rewrites_instance_reference(self):
        source = _consumer("GameManager.Instance")
        result = rewrite_singleton_access(
            source,
            singletons={"GameManager"},
            current_classes=set(),
        )
        assert "GameManager.Instance" not in result

    def test_access_uses_camelcase_field(self):
        source = _consumer("GameManager.Instance")
        result = rewrite_singleton_access(
            source,
            singletons={"GameManager"},
            current_classes=set(),
        )
        assert "gameManager.score" in result

    def test_field_name_is_camelcase_of_class(self):
        source = """\
public class Foo : MonoBehaviour
{
    void Update()
    {
        ScoreTracker.Instance.Reset();
    }
}
"""
        result = rewrite_singleton_access(
            source,
            singletons={"ScoreTracker"},
            current_classes=set(),
        )
        # camelCase of ScoreTracker is scoreTracker
        assert "[SerializeField] private ScoreTracker scoreTracker;" in result
        assert "scoreTracker.Reset()" in result

    def test_multiple_accesses_all_rewritten(self):
        source = """\
public class HUD : MonoBehaviour
{
    void Update()
    {
        int s = GameManager.Instance.score;
        int l = GameManager.Instance.level;
        bool a = GameManager.Instance.active;
    }
}
"""
        result = rewrite_singleton_access(
            source,
            singletons={"GameManager"},
            current_classes=set(),
        )
        assert "GameManager.Instance" not in result
        # All three accesses rewritten
        assert result.count("gameManager.") >= 3

    def test_serializefield_injected_only_once_per_class(self):
        source = """\
public class HUD : MonoBehaviour
{
    void Update()
    {
        int s = GameManager.Instance.score;
        int l = GameManager.Instance.level;
    }
}
"""
        result = rewrite_singleton_access(
            source,
            singletons={"GameManager"},
            current_classes=set(),
        )
        # Must appear exactly once, not duplicated
        assert result.count("[SerializeField] private GameManager gameManager;") == 1


# ===========================================================================
# 4. Singleton's own class is NOT rewritten
# ===========================================================================

class TestOwnClassSkipped:
    """The singleton's own file must NOT have its Instance references rewritten.
    GameManager needs GameManager.Instance = this internally."""

    def test_own_class_not_rewritten(self):
        source = """\
public class GameManager : MonoBehaviour
{
    // Singleton — wire via Inspector [SerializeField] on dependents
    public static GameManager Instance;

    void Awake()
    {
        GameManager.Instance = this;
    }
}
"""
        result = rewrite_singleton_access(
            source,
            singletons={"GameManager"},
            current_classes={"GameManager"},
        )
        # The initialization must survive unchanged
        assert "GameManager.Instance = this;" in result

    def test_own_class_gets_no_serializefield_injection(self):
        source = """\
public class GameManager : MonoBehaviour
{
    public static GameManager Instance;

    void Awake()
    {
        GameManager.Instance = this;
    }
}
"""
        result = rewrite_singleton_access(
            source,
            singletons={"GameManager"},
            current_classes={"GameManager"},
        )
        # The rewriter must not inject a SerializeField into the singleton itself
        assert "[SerializeField] private GameManager gameManager;" not in result


# ===========================================================================
# 5. Idempotence contract
# ===========================================================================

class TestIdempotence:
    """Applying rewrite_singleton_access twice must produce the same result
    as applying it once."""

    def test_idempotent_on_consumer(self):
        source = _consumer("GameManager.Instance")
        once = rewrite_singleton_access(
            source,
            singletons={"GameManager"},
            current_classes=set(),
        )
        twice = rewrite_singleton_access(
            once,
            singletons={"GameManager"},
            current_classes=set(),
        )
        assert once == twice

    def test_idempotent_on_already_rewritten(self):
        """If the field already exists, do not inject a second copy."""
        already_rewritten = """\
public class PlayerController : MonoBehaviour
{
    [SerializeField] private GameManager gameManager;

    void Update()
    {
        int s = gameManager.score;
    }
}
"""
        result = rewrite_singleton_access(
            already_rewritten,
            singletons={"GameManager"},
            current_classes=set(),
        )
        # Still no double-injection
        assert result.count("[SerializeField] private GameManager gameManager;") == 1

    def test_no_serializefield_leak_when_no_instance_ref(self):
        """If the file has no ClassName.Instance reference, skip injection."""
        source = """\
public class Foo : MonoBehaviour
{
    void Update()
    {
        int x = 1;
    }
}
"""
        result = rewrite_singleton_access(
            source,
            singletons={"GameManager"},
            current_classes=set(),
        )
        assert "[SerializeField]" not in result
        assert result == source


# ===========================================================================
# 6. Multi-singleton contract
# ===========================================================================

class TestMultipleSingletons:
    """Multiple singletons in the singletons set must each be handled
    independently."""

    def test_two_singletons_both_injected(self):
        source = """\
public class HUD : MonoBehaviour
{
    void Update()
    {
        int s = GameManager.Instance.score;
        int a = AudioManager.Instance.volume;
    }
}
"""
        result = rewrite_singleton_access(
            source,
            singletons={"GameManager", "AudioManager"},
            current_classes=set(),
        )
        assert "[SerializeField] private GameManager gameManager;" in result
        assert "[SerializeField] private AudioManager audioManager;" in result
        assert "GameManager.Instance" not in result
        assert "AudioManager.Instance" not in result

    def test_own_class_skipped_other_singletons_rewritten(self):
        """If current_classes contains one singleton but not another, only
        the foreign singleton gets rewritten."""
        source = """\
public class GameManager : MonoBehaviour
{
    public static GameManager Instance;

    void Awake()
    {
        GameManager.Instance = this;
        int v = AudioManager.Instance.volume;
    }
}
"""
        result = rewrite_singleton_access(
            source,
            singletons={"GameManager", "AudioManager"},
            current_classes={"GameManager"},
        )
        # GameManager.Instance = this; must survive
        assert "GameManager.Instance = this;" in result
        # AudioManager.Instance should be rewritten
        assert "AudioManager.Instance" not in result
        assert "[SerializeField] private AudioManager audioManager;" in result
