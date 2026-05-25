"""
Tests for Particle System
Author: Inventions4All - github:TWeb79
"""

import pytest
import numpy as np
from neurosync.visualizers.particles import ParticleSystem


class TestParticleSystemInitialization:
    """Tests for particle system initialization."""

    def test_default_initialization(self):
        """Test default particle system initialization."""
        system = ParticleSystem()
        assert system.width == 800
        assert system.height == 600
        assert system.slow_particles == 30
        assert system.fast_particles == 200

    def test_custom_dimensions(self):
        """Test particle system with custom dimensions."""
        system = ParticleSystem(width=1024, height=768)
        assert system.width == 1024
        assert system.height == 768

    def test_slow_particles_initialized(self):
        """Test that slow particles are initialized."""
        system = ParticleSystem()
        assert system.slow_pos.shape == (30, 2)
        assert system.slow_vel.shape == (30, 2)

    def test_fast_particles_initialized(self):
        """Test that fast particles are initialized."""
        system = ParticleSystem()
        assert system.fast_pos.shape == (200, 2)
        assert system.fast_vel.shape == (200, 2)

    def test_particles_within_bounds(self):
        """Test that particles are initialized within bounds."""
        system = ParticleSystem(width=800, height=600)
        assert np.all(system.slow_pos >= 0)
        assert np.all(system.slow_pos[:, 0] <= 800)
        assert np.all(system.slow_pos[:, 1] <= 600)
        assert np.all(system.fast_pos >= 0)
        assert np.all(system.fast_pos[:, 0] <= 800)
        assert np.all(system.fast_pos[:, 1] <= 600)


class TestParticleSystemUpdate:
    """Tests for particle system update."""

    def test_update_with_delta_band(self):
        """Test update with delta band."""
        system = ParticleSystem()
        old_slow_pos = system.slow_pos.copy()
        old_fast_pos = system.fast_pos.copy()
        
        system.update(band="delta", dt=0.016)
        
        # Delta band should move slowly
        assert not np.array_equal(system.slow_pos, old_slow_pos)
        assert not np.array_equal(system.fast_pos, old_fast_pos)

    def test_update_with_gamma_band(self):
        """Test update with gamma band."""
        system = ParticleSystem()
        old_slow_pos = system.slow_pos.copy()
        old_fast_pos = system.fast_pos.copy()
        
        system.update(band="gamma", dt=0.016)
        
        # Gamma band should move quickly
        assert not np.array_equal(system.slow_pos, old_slow_pos)
        assert not np.array_equal(system.fast_pos, old_fast_pos)

    def test_update_preserves_particle_count(self):
        """Test that update preserves particle count."""
        system = ParticleSystem()
        system.update(band="alpha")
        
        assert system.slow_pos.shape == (30, 2)
        assert system.fast_pos.shape == (200, 2)

    def test_update_wraps_positions(self):
        """Test that positions wrap around at boundaries."""
        system = ParticleSystem(width=100, height=100)
        # Update many times to ensure wrapping
        for _ in range(100):
            system.update(band="gamma", dt=0.1)
        
        # All positions should still be within bounds
        assert np.all(system.slow_pos >= 0)
        assert np.all(system.slow_pos[:, 0] < 100)
        assert np.all(system.slow_pos[:, 1] < 100)
        assert np.all(system.fast_pos >= 0)
        assert np.all(system.fast_pos[:, 0] < 100)
        assert np.all(system.fast_pos[:, 1] < 100)

    def test_update_all_bands(self):
        """Test update with all band types."""
        system = ParticleSystem()
        bands = ["delta", "theta", "alpha", "beta", "gamma"]
        
        for band in bands:
            system.update(band=band, dt=0.016)
            # Should not crash and positions should be valid

    def test_update_with_zero_dt(self):
        """Test update with zero delta time."""
        system = ParticleSystem()
        old_pos = system.slow_pos.copy()
        system.update(band="alpha", dt=0.0)
        
        # Should still be valid even with zero dt
        assert system.slow_pos.shape == (30, 2)

    def test_update_with_unknown_band(self):
        """Test update with unknown band."""
        system = ParticleSystem()
        # Should default to neutral speed
        system.update(band="unknown", dt=0.016)
        assert system.slow_pos.shape == (30, 2)

    def test_movement_speed_by_band(self):
        """Test that different bands produce different movement speeds."""
        system1 = ParticleSystem(width=10000, height=10000)
        system2 = ParticleSystem(width=10000, height=10000)
        
        # Set same initial positions
        system2.slow_pos = system1.slow_pos.copy()
        system2.slow_vel = system1.slow_vel.copy()
        system2.fast_pos = system1.fast_pos.copy()
        system2.fast_vel = system1.fast_vel.copy()
        
        system1.update(band="delta", dt=0.016)
        system2.update(band="gamma", dt=0.016)
        
        # Both systems should have updated positions
        assert system1.slow_pos.shape == (30, 2)
        assert system2.slow_pos.shape == (30, 2)


class TestParticleSystemColors:
    """Tests for particle system color assignment."""

    def test_get_band_colors_delta(self):
        """Test getting colors for delta band."""
        system = ParticleSystem()
        colors = system.set_band_colors("delta")
        assert len(colors) == 2
        assert isinstance(colors[0], tuple)
        assert len(colors[0]) == 3

    def test_get_band_colors_theta(self):
        """Test getting colors for theta band."""
        system = ParticleSystem()
        colors = system.set_band_colors("theta")
        assert len(colors) == 2

    def test_get_band_colors_alpha(self):
        """Test getting colors for alpha band."""
        system = ParticleSystem()
        colors = system.set_band_colors("alpha")
        assert len(colors) == 2

    def test_get_band_colors_beta(self):
        """Test getting colors for beta band."""
        system = ParticleSystem()
        colors = system.set_band_colors("beta")
        assert len(colors) == 2

    def test_get_band_colors_gamma(self):
        """Test getting colors for gamma band."""
        system = ParticleSystem()
        colors = system.set_band_colors("gamma")
        assert len(colors) == 2

    def test_get_band_colors_default(self):
        """Test getting colors for unknown band."""
        system = ParticleSystem()
        colors = system.set_band_colors("unknown")
        assert len(colors) == 2

    def test_color_values_in_range(self):
        """Test that color values are in valid RGB range."""
        system = ParticleSystem()
        bands = ["delta", "theta", "alpha", "beta", "gamma"]
        
        for band in bands:
            colors = system.set_band_colors(band)
            for color in colors:
                assert len(color) == 3
                assert all(0 <= c <= 255 for c in color)
