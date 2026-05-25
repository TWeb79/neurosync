"""
Tests for Session Controller
Author: Inventions4All - github:TWeb79
"""

import pytest
from neurosync.sessions.controller import SessionController, Preset, PresetCategory, PRESETS, _get_band


class TestGetBand:
    """Tests for _get_band function."""

    def test_get_band_delta(self):
        """Test delta band classification."""
        assert _get_band(2.0) == "Delta"

    def test_get_band_theta(self):
        """Test theta band classification."""
        assert _get_band(6.0) == "Theta"

    def test_get_band_alpha(self):
        """Test alpha band classification."""
        assert _get_band(10.0) == "Alpha"

    def test_get_band_beta(self):
        """Test beta band classification."""
        assert _get_band(20.0) == "Beta"

    def test_get_band_gamma(self):
        """Test gamma band classification."""
        assert _get_band(50.0) == "Gamma"


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

    def test_transition_curve_start(self):
        """Test transition curve at start."""
        controller = SessionController()
        result = controller.get_transition_curve(100.0, 200.0, 0.0)
        assert result == 100.0

    def test_transition_curve_end(self):
        """Test transition curve at end."""
        controller = SessionController()
        result = controller.get_transition_curve(100.0, 200.0, 1.0)
        assert result == 200.0

    def test_get_eased_value_linear(self):
        """Test linear easing."""
        controller = SessionController()
        result = controller.get_eased_value(100.0, 200.0, 0.5, "linear")
        assert result == 150.0

    def test_get_eased_value_ease_in(self):
        """Test ease-in easing."""
        controller = SessionController()
        result = controller.get_eased_value(100.0, 200.0, 0.5, "ease_in")
        assert result == 125.0

    def test_get_eased_value_ease_out(self):
        """Test ease-out easing."""
        controller = SessionController()
        result = controller.get_eased_value(100.0, 200.0, 0.5, "ease_out")
        assert result == 175.0

    def test_get_eased_value_exponential(self):
        """Test exponential easing."""
        controller = SessionController()
        result = controller.get_eased_value(100.0, 200.0, 0.5, "exponential")
        assert 100.0 < result < 200.0

    def test_get_eased_value_default(self):
        """Test default ease-in-out easing."""
        controller = SessionController()
        result = controller.get_eased_value(100.0, 200.0, 0.5)
        assert 100.0 < result < 200.0

    def test_load_preset_with_state_callback(self):
        """Test loading preset triggers state callback."""
        from unittest.mock import MagicMock
        controller = SessionController()
        callback = MagicMock()
        controller.state_changed = callback
        controller.load_preset("deep_sleep")
        callback.assert_called_once_with("Loaded: Deep Sleep")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])