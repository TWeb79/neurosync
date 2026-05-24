"""
Tests for Presets
Author: Inventions4All - github:TWeb79
"""

import pytest
from neurosync.presets.defs import (
    SLEEP_PRESETS,
    FOCUS_PRESETS,
    MEDITATION_PRESETS,
    CREATIVITY_PRESETS,
)


class TestSleepPresets:
    """Tests for sleep presets."""

    def test_deep_sleep_preset(self):
        """Test deep sleep preset values."""
        preset = SLEEP_PRESETS["deep_sleep"]
        assert preset.beat_frequency == 2.0
        assert preset.carrier_frequency == 180.0

    def test_rem_sleep_preset(self):
        """Test REM sleep preset values."""
        preset = SLEEP_PRESETS["rem_sleep"]
        assert preset.beat_frequency == 4.0


class TestFocusPresets:
    """Tests for focus presets."""

    def test_coding_flow_preset(self):
        """Test coding flow preset values."""
        preset = FOCUS_PRESETS["coding_flow"]
        assert preset.beat_frequency == 14.0
        assert preset.carrier_frequency == 220.0


class TestMeditationPresets:
    """Tests for meditation presets."""

    def test_zen_meditation_preset(self):
        """Test zen meditation preset values."""
        preset = MEDITATION_PRESETS["zen_meditation"]
        assert preset.beat_frequency == 7.0


class TestCreativityPresets:
    """Tests for creativity presets."""

    def test_creative_flow_preset(self):
        """Test creative flow preset values."""
        preset = CREATIVITY_PRESETS["creative_flow"]
        assert preset.beat_frequency == 7.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])