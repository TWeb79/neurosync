"""
Visualizer Engine - Realtime Visual Effects
Author: Inventions4All - github:TWeb79
"""

import numpy as np
from scipy.fft import fft
from scipy.signal import get_window


class BrainwaveSphere:
    """Animated orb pulsing at beat frequency."""

    def __init__(self, size: int = 100):
        """Initialize visualizer sphere.

        Args:
            size: Size of the visualization buffer
        """
        self.size = size
        self.amplitude = 0.0
        self.frequency = 0.0

    def update(self, beat_frequency: float, amplitude: float):
        """Update sphere state.

        Args:
            beat_frequency: Current beat frequency
            amplitude: Current signal amplitude
        """
        self.frequency = beat_frequency
        self.amplitude = amplitude


class FrequencyRings:
    """Concentric rings reacting to audio."""

    def __init__(self, num_rings: int = 5):
        """Initialize frequency rings.

        Args:
            num_rings: Number of concentric rings
        """
        self.num_rings = num_rings
        self.ring_values = np.zeros(num_rings)

    def update_from_fft(self, left_channel: np.ndarray, right_channel: np.ndarray):
        """Update ring values from FFT analysis.

        Args:
            left_channel: Left audio channel
            right_channel: Right audio channel
        """
        combined = np.concatenate([left_channel[-1024:], right_channel[-1024:]])
        window = get_window('hann', len(combined))
        windowed_signal = combined * window
        spectrum = np.abs(fft(windowed_signal))[: self.num_rings * 20].reshape(-1, 20).mean(axis=1)
        self.ring_values = spectrum / spectrum.max() if spectrum.max() > 0 else spectrum


class AmbientParticles:
    """Particle system with fixed velocity integration."""

    def __init__(self, num_particles: int = 500):
        """Initialize particle system.

        Args:
            num_particles: Number of particles to simulate
        """
        self.num_particles = num_particles
        self.positions = np.random.rand(num_particles, 2) * 2 - 1
        self.velocities = np.random.rand(num_particles, 2) * 0.01 - 0.005

    def update(self, calmness: float = 1.0, dt: float = 0.016):
        """Update particle positions.

        Args:
            calmness: Calmness factor (0-1)
            dt: Delta time in seconds
        """
        speed = calmness * 0.001
        self.positions += self.velocities * speed * dt
        self.positions = np.clip(self.positions, -1, 1)