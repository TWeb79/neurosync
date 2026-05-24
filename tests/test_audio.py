"""
Tests for Audio Engine
Author: Inventions4All - github:TWeb79
"""

import pytest
import numpy as np
from neurosync.audio.engine import AudioConfig, BrainwaveBand


class TestAudioConfig:
    """Tests for audio configuration."""

    def test_default_config(self):
        """Test default audio configuration."""
        config = AudioConfig()
        assert config.sample_rate == 44100
        assert config.buffer_size == 1024
        assert config.channels == 2

    def test_custom_config(self):
        """Test custom audio configuration."""
        config = AudioConfig(sample_rate=48000, buffer_size=512)
        assert config.sample_rate == 48000
        assert config.buffer_size == 512


class TestBrainwaveBand:
    """Tests for brainwave band enum."""

    def test_delta_range(self):
        """Test delta frequency range."""
        assert BrainwaveBand.DELTA.value == (0.5, 4.0)

    def test_gamma_range(self):
        """Test gamma frequency range."""
        assert BrainwaveBand.GAMMA.value == (30.0, 80.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])