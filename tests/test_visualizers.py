"""
Tests for Visualizer Engine
Author: Inventions4All - github:TWeb79
"""

import pytest
import numpy as np
from neurosync.visualizers.engine import BrainwaveSphere, FrequencyRings, AmbientParticles


class TestBrainwaveSphere:
    """Tests for brainwave sphere visualizer."""

    def test_sphere_initialization(self):
        """Test sphere is initialized correctly."""
        sphere = BrainwaveSphere(size=50)
        assert sphere.size == 50
        assert sphere.amplitude == 0.0
        assert sphere.frequency == 0.0

    def test_sphere_update(self):
        """Test sphere state updates."""
        sphere = BrainwaveSphere()
        sphere.update(10.0, 0.8)
        assert sphere.frequency == 10.0
        assert sphere.amplitude == 0.8


class TestFrequencyRings:
    """Tests for frequency rings visualizer."""

    def test_rings_initialization(self):
        """Test rings are initialized."""
        rings = FrequencyRings(num_rings=5)
        assert rings.num_rings == 5
        assert len(rings.ring_values) == 5

    def test_rings_update_from_fft(self):
        """Test FFT update works."""
        rings = FrequencyRings(num_rings=3)
        left = np.sin(np.linspace(0, 10, 100))
        right = np.cos(np.linspace(0, 10, 100))
        rings.update_from_fft(left, right)
        assert not np.isnan(rings.ring_values).any()


class TestAmbientParticles:
    """Tests for ambient particle system."""

    def test_particles_initialization(self):
        """Test particles are initialized."""
        particles = AmbientParticles(num_particles=100)
        assert particles.num_particles == 100
        assert particles.positions.shape == (100, 2)

    def test_particles_update(self):
        """Test particle positions update."""
        particles = AmbientParticles(num_particles=500)
        old_positions = particles.positions.copy()
        particles.update(calmness=0.5, dt=1.0)
        moved = np.abs(particles.positions - old_positions).sum()
        assert moved > 0.001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])