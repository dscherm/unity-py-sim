"""Contract tests for G8 — TagManager.asset empty layer slots use `- ""` scalar.

Derived from Unity 6 YAML parser behavior, NOT from the implementing agent's
test file (tests/exporter/test_tagmanager.py). All assertions are grounded in:
  - Unity 6 TagManager.asset canonical format
  - yaml.safe_load round-trip expectations
  - data/lessons/coplay_generator_gaps.md gap 8

Do NOT read tests/exporter/test_tagmanager.py before adding tests here.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

import yaml

from src.exporter.project_scaffolder import _write_tag_manager


def _get_layers_section(text: str) -> str:
    """Extract lines between 'layers:' and the next top-level key."""
    lines = text.splitlines()
    in_layers = False
    result = []
    for line in lines:
        if line.strip() == "layers:":
            in_layers = True
            continue
        if in_layers:
            # Stop when we hit the next key at the same indentation level
            if line and not line.startswith(" "):
                break
            # Also stop at a new '  key:' peer (not a list item)
            if line.startswith("  ") and not line.startswith("  -") and ":" in line:
                break
            result.append(line)
    return "\n".join(result)


def _load_yaml_body(text: str) -> dict:
    """Strip %YAML / %TAG / '---' directives and load via yaml.safe_load."""
    body_lines = []
    for line in text.splitlines():
        if line.startswith("%") or line.startswith("---"):
            continue
        body_lines.append(line)
    return yaml.safe_load("\n".join(body_lines))


class TestTagManagerUnity6Contract:
    """Verify _write_tag_manager produces Unity 6 compliant TagManager.asset."""

    def _write_and_read(
        self,
        tags: list[str] | None = None,
        layers: dict[str, int] | None = None,
    ) -> tuple[str, dict]:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir)
            (out / "ProjectSettings").mkdir()
            _write_tag_manager(out, tags=tags, layers=layers)
            text = (out / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        parsed = _load_yaml_body(text)
        return text, parsed

    def test_yaml_safe_load_round_trip_produces_tag_manager_key(self):
        """yaml.safe_load must produce a dict with a 'TagManager' key."""
        _, parsed = self._write_and_read()
        assert "TagManager" in parsed, "Top-level key 'TagManager' missing after yaml.safe_load"

    def test_yaml_safe_load_serialized_version_is_2(self):
        """TagManager.serializedVersion must equal 2."""
        _, parsed = self._write_and_read()
        assert parsed["TagManager"]["serializedVersion"] == 2

    def test_yaml_safe_load_has_tags_key(self):
        """TagManager must contain a 'tags' key after yaml.safe_load."""
        _, parsed = self._write_and_read()
        assert "tags" in parsed["TagManager"]

    def test_layers_array_has_exactly_32_entries(self):
        """Unity requires exactly 32 layer slots."""
        _, parsed = self._write_and_read()
        layers = parsed["TagManager"]["layers"]
        assert len(layers) == 32, f"Expected 32 layer slots, got {len(layers)}"

    def test_no_bare_null_scalar_in_layers_section(self):
        """No line in the layers section should be a bare `  -` null scalar.

        Unity 6 rejects bare `-` with 'Parser Failure: Expect : between key
        and value within mapping'. Only `  - ""` is valid for empty slots.
        """
        text, _ = self._write_and_read()
        layers_section = _get_layers_section(text)
        # A bare null scalar line is `  -` with nothing after (or just whitespace)
        bare_null = re.compile(r"^\s*-\s*$", re.MULTILINE)
        matches = bare_null.findall(layers_section)
        assert not matches, (
            f"Found {len(matches)} bare `-` null scalar(s) in layers section — "
            "Unity 6 requires `- \"\"` for empty slots"
        )

    def test_layer_index_3_is_empty_string_not_none(self):
        """Index 3 is a Unity reserved slot — must parse as '' not None."""
        _, parsed = self._write_and_read()
        layers = parsed["TagManager"]["layers"]
        val = layers[3]
        assert val is not None, "Layer index 3 parsed as None — bare `-` null scalar in output"
        assert val == "", f"Layer index 3 expected empty string, got {val!r}"

    def test_layer_index_6_is_empty_string_not_none(self):
        """Index 6 is another Unity reserved slot — must parse as '' not None."""
        _, parsed = self._write_and_read()
        layers = parsed["TagManager"]["layers"]
        val = layers[6]
        assert val is not None, "Layer index 6 parsed as None"
        assert val == "", f"Layer index 6 expected empty string, got {val!r}"

    def test_builtin_layers_at_correct_indices(self):
        """Builtin layers 0,1,2,4,5 must survive round-trip at their indices."""
        _, parsed = self._write_and_read()
        layers = parsed["TagManager"]["layers"]
        assert layers[0] == "Default"
        assert layers[1] == "TransparentFX"
        assert layers[2] == "Ignore Raycast"
        assert layers[4] == "Water"
        assert layers[5] == "UI"

    def test_custom_layers_at_arbitrary_indices(self):
        """Custom layers at indices 10, 20, 28 survive round-trip."""
        custom = {"Alpha": 10, "Beta": 20, "Gamma": 28}
        _, parsed = self._write_and_read(layers=custom)
        layers = parsed["TagManager"]["layers"]
        assert layers[10] == "Alpha"
        assert layers[20] == "Beta"
        assert layers[28] == "Gamma"

    def test_custom_layers_still_produce_exactly_32_slots(self):
        """Adding custom layers must not change the total count from 32."""
        custom = {"Alpha": 10, "Beta": 20, "Gamma": 28}
        _, parsed = self._write_and_read(layers=custom)
        assert len(parsed["TagManager"]["layers"]) == 32

    def test_empty_slots_between_custom_layers_are_empty_string(self):
        """Slots not assigned to builtin or custom layers parse as empty string."""
        custom = {"Alpha": 10}
        _, parsed = self._write_and_read(layers=custom)
        layers = parsed["TagManager"]["layers"]
        # Slot 11 is neither builtin nor custom
        assert layers[11] == "", f"Slot 11 expected '' got {layers[11]!r}"
        # Slot 31 at the end
        assert layers[31] == "", f"Slot 31 expected '' got {layers[31]!r}"

    def test_tags_section_includes_default_unity_tags(self):
        """Default Unity tags must appear in the tags list."""
        _, parsed = self._write_and_read()
        tags = parsed["TagManager"]["tags"]
        for expected in ("Untagged", "Respawn", "Finish", "Player"):
            assert expected in tags, f"Default tag '{expected}' missing"

    def test_custom_tags_merged_into_tags_section(self):
        """Custom tags provided to _write_tag_manager appear in parsed tags."""
        _, parsed = self._write_and_read(tags=["Enemy", "Pickup"])
        tags = parsed["TagManager"]["tags"]
        assert "Enemy" in tags
        assert "Pickup" in tags

    def test_sorting_layers_section_present(self):
        """m_SortingLayers key must survive round-trip."""
        _, parsed = self._write_and_read()
        assert "m_SortingLayers" in parsed["TagManager"]

    def test_output_file_ends_with_newline(self):
        """Unity asset files must end with a newline character."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir)
            (out / "ProjectSettings").mkdir()
            _write_tag_manager(out, tags=None, layers=None)
            text = (out / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        assert text.endswith("\n"), "TagManager.asset must end with a newline"
