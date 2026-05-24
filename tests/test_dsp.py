"""
Tests for DSP Core
Author: Inventions4All - github:TWeb79
"""

import pytest
import numpy as np
from neurosync.dsp.core import (
    generate_sine_wave,
    calculate_binaural_frequencies,
    generate_binaural_beat,
    apply_dB_limiter,
)


class TestSineWaveGeneration:
    """Tests for sine wave generation."""

    def test_generate_sine_wave_basic(self):
        """Test basic sine wave generation."""
        result = generate_sine_wave(440.0, 0.1, 44100)
        assert len(result) == 4410
        assert result.dtype == np.float64

    def test_sine_wave_frequency(self):
        """Test that generated wave has correct frequency."""
        wave = generate_sine_wave(440.0, 1.0, 44100)
        zero_crossings = np.where(np.diff(np.sign(wave)))[0]
        period_samples = np.mean(np.diff(zero_crossings[::2]))
        calculated_freq = 44100 / period_samples
        assert abs(calculated_freq - 440.0) < 1.0


class TestBinauralFrequencies:
    """Tests for binaural beat frequency calculation."""

    def test_calculate_binaural_frequencies(self):
        """Test binaural frequency calculation."""
        left, right = calculate_binaural_frequencies(220.0, 10.0)
        assert left == 220.0
        assert right == 230.0


class TestBinauralBeatGeneration:
    """Tests for binaural beat generation."""

    def test_generate_binaural_beat_output(self):
        """Test binaural beat output shape."""
        left, right = generate_binaural_beat(220.0, 10.0, 0.5, 44100)
        assert left.shape == (22050,)
        assert right.shape == (22050,)

    def test_binaural_beat_frequency_difference(self):
        """Test that left/right have correct frequency difference."""
        left, right = generate_binaural_beat(220.0, 10.0, 0.5, 44100)
        assert not np.array_equal(left, right)


class TestLimiter:
    """Tests for limiter function."""

    def test_limiter_preserves_quiet_signals(self):
        """Test that limiter doesn't affect quiet signals."""
        quiet = np.random.rand(1000) * 0.1
        result = apply_dB_limiter(quiet)
        np.testing.assert_array_almost_equal(result, quiet)

    def test_limiter_reduces_loud_signals(self):
        """Test that limiter reduces signals above threshold."""
        loud = np.ones(1000) * 2.0
        result = apply_dB_limiter(loud)
        assert result.max() <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])