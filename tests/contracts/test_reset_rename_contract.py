"""Contract tests: Python reset() must translate to C# ResetState(), not Reset().

Unity's built-in Reset() is a lifecycle method called by the editor during
AddComponent, causing NullReferenceException if user code runs there.
The translator must rename user-defined reset() to ResetState().
"""
from src.translator.python_to_csharp import translate
from src.translator.python_parser import parse_python


def _translate(python_code: str) -> str:
    """Helper to translate Python source to C# string."""
    parsed = parse_python(python_code)
    return translate(parsed)


class TestResetMethodRename:
    """def reset(self) must become void ResetState(), not void Reset()."""

    def test_reset_method_becomes_reset_state(self):
        code = '''
from src.engine import MonoBehaviour

class GameManager(MonoBehaviour):
    def awake(self):
        self.score = 0

    def reset(self):
        self.score = 0
'''
        result = _translate(code)
        assert "void ResetState()" in result, f"Expected ResetState(), got:\n{result}"
        # Must NOT contain a bare Reset() method declaration
        # (Unity lifecycle Reset() should not appear for user reset())
        assert "void Reset()" not in result, f"Must not emit Reset(), got:\n{result}"

    def test_self_reset_call_becomes_reset_state(self):
        code = '''
from src.engine import MonoBehaviour

class GameManager(MonoBehaviour):
    def awake(self):
        self.score = 0

    def reset(self):
        self.score = 0

    def update(self):
        self.reset()
'''
        result = _translate(code)
        # The call should be ResetState(), not Reset()
        assert "ResetState()" in result, f"Expected ResetState() call, got:\n{result}"
        # Check the method body in Update contains ResetState
        assert "Reset()" not in result or "ResetState()" in result

    def test_external_reset_call_becomes_reset_state(self):
        code = '''
from src.engine import MonoBehaviour

class Player(MonoBehaviour):
    def awake(self):
        self.game_manager = None

    def update(self):
        self.game_manager.reset()
'''
        result = _translate(code)
        assert "ResetState()" in result, f"Expected gameManager.ResetState(), got:\n{result}"

    def test_lifecycle_methods_not_renamed(self):
        """Awake, Start, Update etc. must keep their Unity names."""
        code = '''
from src.engine import MonoBehaviour

class Foo(MonoBehaviour):
    def awake(self):
        pass
    def start(self):
        pass
    def update(self):
        pass
    def fixed_update(self):
        pass
'''
        result = _translate(code)
        assert "void Awake()" in result
        assert "void Start()" in result
        assert "void Update()" in result
        assert "void FixedUpdate()" in result

    def test_reset_state_no_double_rename(self):
        """A method already named reset_state() should become ResetState(), not ResetStateState()."""
        code = '''
from src.engine import MonoBehaviour

class Foo(MonoBehaviour):
    def reset_state(self):
        pass
'''
        result = _translate(code)
        assert "ResetState()" in result
        assert "ResetStateState()" not in result
