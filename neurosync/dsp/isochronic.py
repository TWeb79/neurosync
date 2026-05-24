"""
Isochronic Tones - Speaker-compatible entrainment
Author: Inventions4All - github:TWeb79
"""

import numpy as np


class IsochronicGenerator:
    """Generates isochronic tones for speaker-compatible entrainment.

    Isochronic tones are amplitude-modulated carriers at the beat frequency.
    Unlike binaural beats, they work on speakers without headphones.
    """

    def __init__(self, sample_rate: int = 44100):
        """Initialize isochronic generator.

        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate

    def generate(
        self, carrier_freq: float, beat_freq: float, duration: float, duty: float = 0.5
    ) -> np.ndarray:
        """Generate isochronic tone.

        Args:
            carrier_freq: Carrier frequency in Hz
            beat_freq: Pulse rate (beats per second)
            duration: Duration in seconds
            duty: Duty cycle (0.0-1.0), default 50%

        Returns:
            Isochronic tone samples
        """
        num_samples = int(self.sample_rate * duration)
        t = np.arange(num_samples) / self.sample_rate
        envelope = np.sin(np.pi * beat_freq * t) ** 2
        envelope = np.clip(envelope, 0, 1)
        return np.sin(2 * np.pi * carrier_freq * t) * envelope