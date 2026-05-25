"""
Particle System for Visualizers
Author: Inventions4All - github:TWeb79
"""

import numpy as np


class ParticleSystem:
    """Upgraded particle system with band-aware behavior."""

    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.slow_particles = 30
        self.fast_particles = 200
        self._init_particles()

    def _init_particles(self):
        self.slow_pos = np.random.rand(self.slow_particles, 2) * np.array([self.width, self.height])
        self.slow_vel = np.random.rand(self.slow_particles, 2) * 2 - 1
        self.fast_pos = np.random.rand(self.fast_particles, 2) * np.array([self.width, self.height])
        self.fast_vel = np.random.rand(self.fast_particles, 2) * 4 - 2

    def update(self, band: str = "alpha", dt: float = 0.016):
        """Update particle positions based on brainwave band.

        Args:
            band: Current brainwave band (delta, theta, alpha, beta, gamma)
            dt: Delta time in seconds
        """
        speed_mult = {"delta": 0.3, "theta": 0.6, "alpha": 1.0, "beta": 1.5, "gamma": 2.0}
        speed = speed_mult.get(band, 1.0)

        self.slow_pos += self.slow_vel * speed * 0.5 * dt
        self.fast_pos += self.fast_vel * speed * dt

        self.slow_pos = np.mod(self.slow_pos, [self.width, self.height])
        self.fast_pos = np.mod(self.fast_pos, [self.width, self.height])

    def set_band_colors(self, band: str) -> tuple[tuple[int, int, int], ...]:
        """Get particle colors for current band."""
        colors: dict[str, tuple[tuple[int, int, int], ...]] = {
            "delta": ((10, 20, 80), (30, 50, 120)),
            "theta": ((80, 40, 150), (150, 80, 200)),
            "alpha": ((0, 200, 220), (0, 150, 180)),
            "beta": ((16, 185, 129), (30, 200, 150)),
            "gamma": ((244, 63, 94), (255, 100, 130)),
        }
        return colors.get(band, ((0, 200, 220), (0, 150, 180)))