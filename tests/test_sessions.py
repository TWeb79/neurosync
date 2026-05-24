"""
Tests for Session Controller
Author: Inventions4All - github:TWeb79
"""

import pytest
from neurosync.sessions.controller import SessionController, Preset, PresetCategory, PRESETS


class TestPresets:
    """Tests for preset definitions."""

    def test_presets_exist(self):
        """Test that presets are defined."""
        assert len(PRESETS) > 0

    def test_sleep_presets(self):
        """Test sleep presets are defined."""
        assert "deep_sleep" in PRESETS
        assert PRESETS["deep_sleep"].category == PresetCategory.SLEEP

    def test_focus_presets(self):
        """Test focus presets are defined."""
        assert "coding_flow" in PRESETS
        assert PRESETS["coding_flow"].category == PresetCategory.FOCUS


class TestSessionController:
    """Tests for session controller."""

    def test_load_preset(self):
        """Test loading a preset."""
        controller = SessionController()
        preset = controller.load_preset("deep_sleep")
        assert preset.name == "Deep Sleep"
        assert preset.beat_frequency == 2.0

    def test_load_invalid_preset(self):
        """Test loading invalid preset raises error."""
        controller = SessionController()
        with pytest.raises(KeyError):
            controller.load_preset("nonexistent")

    def test_transition_curve(self):
        """Test transition curve smoothing."""
        controller = SessionController()
        result = controller.get_transition_curve(100.0, 200.0, 0.5)
        assert 100.0 < result < 200.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])