"""
Harmonic Layer - Isochronic tones, ambient pads, noise generators
Author: Inventions4All - github:TWeb79
"""

import numpy as np


class IsochronicGenerator:
    """Generates isochronic tones for speaker-compatible entrainment."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def generate(
        self, carrier_freq: float, beat_freq: float, duration: float, duty: float = 0.5
    ) -> np.ndarray:
        """Generate isochronic tone.

        Args:
            carrier_freq: Carrier frequency in Hz
            beat_freq: Pulse rate in Hz
            duration: Duration in seconds
            duty: Duty cycle (0.0-1.0)

        Returns:
            Isochronic tone samples
        """
        num_samples = int(self.sample_rate * duration)
        t = np.arange(num_samples) / self.sample_rate
        envelope = np.sin(np.pi * beat_freq * t) ** 2
        envelope = np.clip(envelope, 0, 1)
        return np.sin(2 * np.pi * carrier_freq * t) * envelope


class HarmonicLayer:
    """Generative harmonic stack for warmth."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.harmonics = [
            (1.0, 1.0),
            (2.0, 0.35),
            (3.0, 0.15),
            (4.0, 0.08),
            (5.0, 0.04),
        ]

    def generate(self, carrier_freq: float, duration: float) -> np.ndarray:
        """Generate harmonic stack with overtones.

        Args:
            carrier_freq: Fundamental frequency
            duration: Duration in seconds

        Returns:
            Harmonic stack samples
        """
        num_samples = int(self.sample_rate * duration)
        t = np.arange(num_samples) / self.sample_rate
        signal = np.zeros(num_samples)
        for mult, amp in self.harmonics:
            signal += amp * np.sin(2 * np.pi * carrier_freq * mult * t)
        return signal / len(self.harmonics)


class AmbientPadLayer:
    """Ambient pad synthesizer for atmospheric background."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self._phase = 0.0
        self._base_freq = 110.0
        self._detunes = [0.9983, 0.9996, 1.0004, 1.0017]
        self._lfo_phase = 0.0

    def generate(self, duration: float, base_freq: float = 110.0) -> np.ndarray:
        """Generate ambient pad with detuned voices.

        Args:
            duration: Duration in seconds
            base_freq: Base frequency for the pad

        Returns:
            Ambient pad samples
        """
        num_samples = int(self.sample_rate * duration)
        t = np.arange(num_samples) / self.sample_rate
        self._lfo_phase += num_samples / self.sample_rate * 0.05
        lfo = np.sin(2 * np.pi * self._lfo_phase)
        detune_mod = lfo * 0.015
        signal = np.zeros(num_samples)
        for detune in self._detunes:
            freq = base_freq * detune * (1 + detune_mod)
            signal += np.sin(2 * np.pi * freq * t)
        return signal / len(self._detunes) * 0.3


class PinkNoiseGenerator:
    """Pink noise generator using Voss algorithm."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def generate(self, duration: float) -> np.ndarray:
        """Generate pink noise.

        Args:
            duration: Duration in seconds

        Returns:
            Pink noise samples
        """
        num_samples = int(self.sample_rate * duration)
        white = np.random.randn(num_samples)
        pink = np.zeros(num_samples)
        pink[0] = white[0]
        for i in range(1, num_samples):
            pink[i] = 0.997 * pink[i - 1] + 0.03 * white[i]
        return pink


class SubBassPulseGenerator:
    """Sub-bass pulse generator for house music integration."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self._step = 0
        self._sub_bass_freq = 50.0
        self._bpm = 60

    def generate(self, duration: float, bpm: float = 60.0) -> np.ndarray:
        """Generate sub-bass pulse with 4/4 kick pattern.

        Args:
            duration: Duration in seconds
            bpm: Beats per minute for the pulse

        Returns:
            Sub-bass pulse samples
        """
        num_samples = int(self.sample_rate * duration)
        t = np.arange(num_samples) / self.sample_rate
        
        # 4/4 kick pattern: 1.0, 0.0, 0.7, 0.0, 1.0, 0.0, 0.7, 0.0 (8 steps per bar)
        # Each step is a 16th note
        seconds_per_beat = 60.0 / bpm
        seconds_per_step = seconds_per_beat / 2.0  # 16th notes
        samples_per_step = int(self.sample_rate * seconds_per_step)
        
        # Pattern repeats every 8 steps (2 bars of 16th notes)
        pattern = [1.0, 0.0, 0.7, 0.0, 1.0, 0.0, 0.7, 0.0]
        
        signal = np.zeros(num_samples)
        
        for i, amp in enumerate(pattern):
            start_sample = i * samples_per_step
            end_sample = min((i + 1) * samples_per_step, num_samples)
            if start_sample < num_samples:
                # Create smooth ramp (cosine) for each step
                step_t = np.arange(end_sample - start_sample) / max(1, samples_per_step - 1)
                ramp = 0.5 * (1 - np.cos(np.pi * step_t))  # Cosine rise/fall
                signal[start_sample:end_sample] += amp * ramp * np.sin(2 * np.pi * self._sub_bass_freq * t[start_sample:end_sample])
        
        return signal * 0.08  # Very low gain - felt not heard