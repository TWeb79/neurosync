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
    BinauralGenerator,
)
from neurosync.dsp.harmonic import IsochronicGenerator, HarmonicLayer, PinkNoiseGenerator


class TestSineWaveGeneration:
    """Tests for sine wave generation."""

    def test_generate_sine_wave_basic(self):
        result = generate_sine_wave(440.0, 0.1, 44100)
        assert len(result) == 4410
        assert result.dtype == np.float64

    def test_sine_wave_frequency(self):
        wave = generate_sine_wave(440.0, 1.0, 44100)
        zero_crossings = np.where(np.diff(np.sign(wave)))[0]
        period_samples = np.mean(np.diff(zero_crossings[::2]))
        calculated_freq = 44100 / period_samples
        assert abs(calculated_freq - 440.0) < 1.0


class TestBinauralFrequencies:
    """Tests for binaural beat frequency calculation."""

    def test_calculate_binaural_frequencies(self):
        left, right = calculate_binaural_frequencies(220.0, 10.0)
        assert left == 220.0
        assert right == 230.0


class TestBinauralGenerator:
    """Tests for stateful BinauralGenerator."""

    def test_generator_initialization(self):
        gen = BinauralGenerator()
        assert gen.sample_rate == 44100
        assert gen._phase_left == 0.0
        assert gen._phase_right == 0.0

    def test_phase_continuity(self):
        gen = BinauralGenerator(sample_rate=44100)
        left1, right1 = gen.generate_frame(220.0, 10.0, 1024)
        left2, right2 = gen.generate_frame(220.0, 10.0, 1024)
        assert len(left1) == 1024
        assert len(left2) == 1024
        consecutive = np.concatenate([left1[-100:], left2[:100]])
        assert consecutive.dtype == np.float64

    def test_frequency_glide(self):
        gen = BinauralGenerator()
        gen.set_target_beat(20.0)
        for _ in range(50000):
            gen.generate_frame(220.0, 10.0, 1024)
        assert abs(gen._beat_current - 20.0) < 0.5

    def test_current_frequencies(self):
        gen = BinauralGenerator()
        gen.set_target_beat(15.0)
        freqs = gen.get_current_frequencies()
        assert "carrier" in freqs
        assert "beat" in freqs
        assert "left" in freqs
        assert "right" in freqs


class TestIsochronicGenerator:
    """Tests for isochronic tone generation."""

    def test_isochronic_output(self):
        gen = IsochronicGenerator()
        signal = gen.generate(220.0, 10.0, 1.0)
        assert len(signal) == 44100
        assert signal.dtype == np.float64

    def test_isochronic_duty_cycle(self):
        gen = IsochronicGenerator()
        signal1 = gen.generate(220.0, 10.0, 1.0, duty=0.5)
        signal2 = gen.generate(220.0, 10.0, 1.0, duty=0.25)
        assert len(signal1) == len(signal2)


class TestHarmonicLayer:
    """Tests for harmonic stack generation."""

    def test_harmonic_stack(self):
        gen = HarmonicLayer()
        signal = gen.generate(220.0, 1.0)
        assert len(signal) == 44100
        assert signal.dtype == np.float64
        assert np.max(np.abs(signal)) <= 1.0


class TestPinkNoiseGenerator:
    """Tests for pink noise generation."""

    def test_noise_output(self):
        gen = PinkNoiseGenerator()
        noise = gen.generate(1.0)
        assert len(noise) == 44100
        assert noise.dtype == np.float64


class TestBinauralBeatGeneration:
    """Tests for binaural beat generation."""

    def test_generate_binaural_beat_output(self):
        left, right = generate_binaural_beat(220.0, 10.0, 0.5, 44100)
        assert left.shape == (22050,)
        assert right.shape == (22050,)

    def test_binaural_beat_frequency_difference(self):
        left, right = generate_binaural_beat(220.0, 10.0, 0.5, 44100)
        assert not np.array_equal(left, right)


class TestLimiter:
    """Tests for limiter function."""

    def test_limiter_preserves_quiet_signals(self):
        quiet = np.random.rand(1000) * 0.1
        result = apply_dB_limiter(quiet)
        np.testing.assert_array_almost_equal(result, quiet)

    def test_limiter_reduces_loud_signals(self):
        loud = np.ones(1000) * 2.0
        result = apply_dB_limiter(loud)
        assert result.max() <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])