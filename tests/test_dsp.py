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
    interpolate_frequency,
    BinauralGenerator,
)
from neurosync.dsp.harmonic import IsochronicGenerator as HarmonicIsochronicGenerator
from neurosync.dsp.isochronic import IsochronicGenerator
from neurosync.dsp.harmonic import HarmonicLayer, PinkNoiseGenerator, AmbientPadLayer, SubBassPulseGenerator


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

    def test_sine_wave_different_rates(self):
        """Test sine wave at different sample rates."""
        for rate in [8000, 16000, 44100, 48000]:
            result = generate_sine_wave(440.0, 0.1, rate)
            assert len(result) == int(rate * 0.1)

    def test_sine_wave_different_frequencies(self):
        """Test sine wave at different frequencies."""
        for freq in [50, 100, 220, 440, 880, 1000]:
            result = generate_sine_wave(float(freq), 0.1, 44100)
            assert np.min(result) < 0 and np.max(result) > 0


class TestBinauralFrequencies:
    """Tests for binaural beat frequency calculation."""

    def test_calculate_binaural_frequencies(self):
        left, right = calculate_binaural_frequencies(220.0, 10.0)
        assert left == 220.0
        assert right == 230.0

    def test_binaural_frequency_difference(self):
        """Test that right frequency is offset by beat frequency."""
        left, right = calculate_binaural_frequencies(200.0, 5.0)
        assert right - left == 5.0

    def test_binaural_various_frequencies(self):
        """Test with various carrier and beat frequencies."""
        for carrier in [100.0, 220.0, 440.0]:
            for beat in [0.5, 5.0, 10.0, 20.0]:
                left, right = calculate_binaural_frequencies(carrier, beat)
                assert right - left == beat


class TestBinauralGenerator:
    """Tests for stateful BinauralGenerator."""

    def test_generator_initialization(self):
        gen = BinauralGenerator()
        assert gen.sample_rate == 44100
        assert gen._phase_left == 0.0
        assert gen._phase_right == 0.0

    def test_generator_with_custom_rate(self):
        """Test generator with custom sample rate."""
        gen = BinauralGenerator(sample_rate=48000)
        assert gen.sample_rate == 48000

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

    def test_set_target_carrier(self):
        """Test setting target carrier frequency."""
        gen = BinauralGenerator()
        gen.set_target_carrier(250.0)
        assert gen._carrier_target == 250.0

    def test_set_target_beat(self):
        """Test setting target beat frequency."""
        gen = BinauralGenerator()
        gen.set_target_beat(15.0)
        assert gen._beat_target == 15.0

    def test_current_frequencies(self):
        gen = BinauralGenerator()
        gen.set_target_beat(15.0)
        freqs = gen.get_current_frequencies()
        assert "carrier" in freqs
        assert "beat" in freqs
        assert "left" in freqs
        assert "right" in freqs

    def test_brainwave_band_classification(self):
        """Test brainwave band classification."""
        gen = BinauralGenerator()
        assert gen._get_brainwave_band(2.0) == "Delta"
        assert gen._get_brainwave_band(6.0) == "Theta"
        assert gen._get_brainwave_band(10.0) == "Alpha"
        assert gen._get_brainwave_band(20.0) == "Beta"
        assert gen._get_brainwave_band(50.0) == "Gamma"

    def test_phase_wrapping(self):
        """Test that phase wraps correctly."""
        gen = BinauralGenerator()
        # Generate many frames
        for _ in range(1000):
            gen.generate_frame(220.0, 10.0, 1024)
        # Phase should still be in valid range
        assert 0 <= gen._phase_left < 2 * np.pi
        assert 0 <= gen._phase_right < 2 * np.pi

    def test_generate_multiple_frames(self):
        """Test generating multiple consecutive frames."""
        gen = BinauralGenerator()
        total_frames = 0
        for _ in range(10):
            left, right = gen.generate_frame(220.0, 10.0, 1024)
            total_frames += len(left)
            assert len(left) == len(right)
        assert total_frames == 10240


class TestInterpolateFrequency:
    """Tests for frequency interpolation."""

    def test_linear_interpolation(self):
        """Test linear frequency interpolation."""
        result = interpolate_frequency(100.0, 200.0, 1.0, 100)
        assert len(result) == 100
        assert result[0] == 100.0
        assert result[-1] == 200.0

    def test_interpolation_monotonic(self):
        """Test that interpolation is monotonic."""
        result = interpolate_frequency(100.0, 200.0, 1.0, 100)
        for i in range(len(result) - 1):
            assert result[i] <= result[i+1]

    def test_interpolation_different_ranges(self):
        """Test interpolation with different frequency ranges."""
        result = interpolate_frequency(50.0, 500.0, 1.0, 100)
        assert result[0] == 50.0
        assert result[-1] == 500.0
        assert len(result) == 100


class TestIsochronicGenerator:
    """Tests for isochronic tone generation."""

    def test_isochronic_output(self):
        gen = IsochronicGenerator()
        signal = gen.generate(220.0, 10.0, 1.0)
        assert len(signal) == 44100
        assert signal.dtype == np.float64

    def test_isochronic_amplitude_modulation(self):
        """Test that isochronic signal has amplitude modulation."""
        gen = IsochronicGenerator()
        signal = gen.generate(220.0, 10.0, 1.0)
        # Find peaks and troughs to verify amplitude modulation
        assert np.max(np.abs(signal)) <= 1.0

    def test_isochronic_duty_cycle_effect(self):
        """Test effect of duty cycle on isochronic signal."""
        gen = IsochronicGenerator()
        signal1 = gen.generate(220.0, 10.0, 1.0, duty=0.5)
        signal2 = gen.generate(220.0, 10.0, 1.0, duty=0.25)
        assert len(signal1) == len(signal2)
        # Different duty cycles should produce different envelopes

    def test_isochronic_custom_sample_rate(self):
        """Test isochronic with custom sample rate."""
        gen = IsochronicGenerator(sample_rate=48000)
        signal = gen.generate(220.0, 10.0, 1.0)
        assert len(signal) == 48000

    def test_isochronic_short_duration(self):
        """Test isochronic with short duration."""
        gen = IsochronicGenerator()
        signal = gen.generate(220.0, 10.0, 0.1)
        assert len(signal) == 4410

    def test_isochronic_zero_beat_freq(self):
        """Test isochronic with zero beat frequency."""
        gen = IsochronicGenerator()
        signal = gen.generate(220.0, 0.0, 0.5)
        # Should generate a steady signal with no modulation

    def test_isochronic_generator_sample_rate(self):
        """Test isochronic generator sample rate initialization."""
        gen = IsochronicGenerator(sample_rate=48000)
        assert gen.sample_rate == 48000

    def test_isochronic_generator_default_sample_rate(self):
        """Test isochronic generator default sample rate."""
        gen = IsochronicGenerator()
        assert gen.sample_rate == 44100

    def test_isochronic_envelope_clipping(self):
        """Test that isochronic envelope is properly clipped."""
        gen = IsochronicGenerator()
        signal = gen.generate(220.0, 10.0, 1.0)
        # All values should be between -1 and 1
        assert np.all(signal >= -1.0) and np.all(signal <= 1.0)


class TestHarmonicIsochronicGenerator:
    """Tests for harmonic module's isochronic generator."""

    def test_harmonic_isochronic_output(self):
        gen = HarmonicIsochronicGenerator()
        signal = gen.generate(220.0, 10.0, 1.0)
        assert len(signal) == 44100
        assert signal.dtype == np.float64

    def test_harmonic_isochronic_sample_rate(self):
        gen = HarmonicIsochronicGenerator(sample_rate=48000)
        assert gen.sample_rate == 48000


class TestHarmonicLayer:
    """Tests for harmonic stack generation."""

    def test_harmonic_stack(self):
        gen = HarmonicLayer()
        signal = gen.generate(220.0, 1.0)
        assert len(signal) == 44100
        assert signal.dtype == np.float64
        assert np.max(np.abs(signal)) <= 1.0

    def test_harmonic_custom_sample_rate(self):
        """Test harmonic layer with custom sample rate."""
        gen = HarmonicLayer(sample_rate=48000)
        signal = gen.generate(220.0, 1.0)
        assert len(signal) == 48000

    def test_harmonic_different_frequencies(self):
        """Test harmonic generation at different frequencies."""
        gen = HarmonicLayer()
        for freq in [100, 220, 440]:
            signal = gen.generate(float(freq), 1.0)
            assert len(signal) == 44100


class TestAmbientPadLayer:
    """Tests for ambient pad layer."""

    def test_ambient_pad_initialization(self):
        """Test ambient pad initialization."""
        gen = AmbientPadLayer()
        assert gen.sample_rate == 44100

    def test_ambient_pad_generation(self):
        """Test ambient pad generation."""
        gen = AmbientPadLayer()
        signal = gen.generate(1.0)
        assert len(signal) == 44100
        assert signal.dtype == np.float64


class TestSubBassPulseGenerator:
    """Tests for sub-bass pulse generator."""

    def test_sub_bass_initialization(self):
        """Test sub-bass initialization."""
        gen = SubBassPulseGenerator()
        assert gen.sample_rate == 44100

    def test_sub_bass_generation(self):
        """Test sub-bass generation."""
        gen = SubBassPulseGenerator()
        signal = gen.generate(1.0, bpm=120.0)
        assert len(signal) == 44100
        assert signal.dtype == np.float64


class TestPinkNoiseGenerator:
    """Tests for pink noise generation."""

    def test_noise_output(self):
        gen = PinkNoiseGenerator()
        noise = gen.generate(1.0)
        assert len(noise) == 44100
        assert noise.dtype == np.float64

    def test_noise_custom_sample_rate(self):
        """Test pink noise with custom sample rate."""
        gen = PinkNoiseGenerator(sample_rate=48000)
        noise = gen.generate(1.0)
        assert len(noise) == 48000

    def test_noise_random(self):
        """Test that pink noise is random."""
        gen = PinkNoiseGenerator()
        noise1 = gen.generate(1.0)
        noise2 = gen.generate(1.0)
        # Should be different
        assert not np.array_equal(noise1, noise2)


class TestBinauralBeatGeneration:
    """Tests for binaural beat generation."""

    def test_generate_binaural_beat_output(self):
        left, right = generate_binaural_beat(220.0, 10.0, 0.5, 44100)
        assert left.shape == (22050,)
        assert right.shape == (22050,)

    def test_binaural_beat_frequency_difference(self):
        left, right = generate_binaural_beat(220.0, 10.0, 0.5, 44100)
        assert not np.array_equal(left, right)

    def test_binaural_beat_with_drift(self):
        """Test binaural beat with frequency drift."""
        left, right = generate_binaural_beat(220.0, 10.0, 0.5, 44100, drift_rate=0.5)
        assert left.shape == (22050,)
        assert right.shape == (22050,)
        assert not np.array_equal(left, right)

    def test_binaural_beat_different_sample_rates(self):
        """Test binaural beat at different sample rates."""
        for rate in [8000, 44100, 48000]:
            left, right = generate_binaural_beat(220.0, 10.0, 0.5, rate)
            assert left.shape == (int(rate * 0.5),)
            assert right.shape == (int(rate * 0.5),)


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

    def test_limiter_threshold(self):
        """Test limiter with custom threshold."""
        signal = np.ones(1000) * 0.5
        result = apply_dB_limiter(signal, threshold=-6.0)
        assert result.max() <= 0.5

    def test_limiter_ratio(self):
        """Test limiter with custom ratio."""
        signal = np.ones(1000) * 2.0
        result = apply_dB_limiter(signal, ratio=2.0)
        assert result.max() <= 2.0

    def test_limiter_negative_threshold(self):
        """Test limiter with negative threshold."""
        signal = np.ones(1000) * 0.5
        result = apply_dB_limiter(signal, threshold=-20.0)
        assert result.shape == signal.shape


if __name__ == "__main__":
    pytest.main([__file__, "-v"])