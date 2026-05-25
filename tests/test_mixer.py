"""
Tests for Audio Mixer
Author: Inventions4All - github:TWeb79
"""

import pytest
import numpy as np
from neurosync.audio.mixer import AudioMixer, LayerConfig


class TestLayerConfig:
    """Tests for LayerConfig dataclass."""

    def test_default_config(self):
        """Test default layer config."""
        config = LayerConfig()
        assert config.enabled is True
        assert config.gain == 1.0

    def test_custom_config(self):
        """Test custom layer config."""
        config = LayerConfig(enabled=False, gain=0.5)
        assert config.enabled is False
        assert config.gain == 0.5


class TestAudioMixer:
    """Tests for audio mixer."""

    def test_mixer_initialization(self):
        """Test mixer initialization."""
        mixer = AudioMixer()
        assert mixer.sample_rate == 44100
        assert mixer.binaural_gain == 1.0
        assert mixer.isochronic_gain == 0.5

    def test_mixer_with_custom_sample_rate(self):
        """Test mixer with custom sample rate."""
        mixer = AudioMixer(sample_rate=48000)
        assert mixer.sample_rate == 48000

    def test_mix_binaural_only(self):
        """Test mixing binaural signals only."""
        mixer = AudioMixer()
        left = np.sin(np.linspace(0, 2*np.pi, 1000))
        right = np.sin(np.linspace(0, 2*np.pi, 1000))
        
        out_left, out_right = mixer.mix_and_limit(left, right)
        
        assert out_left.shape == left.shape
        assert out_right.shape == right.shape
        assert out_left.dtype == np.float32
        assert out_right.dtype == np.float32

    def test_mix_with_all_layers(self):
        """Test mixing with all layers."""
        mixer = AudioMixer()
        left = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.3
        right = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.3
        isochronic = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.2
        harmonic = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.2
        pad = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.1
        noise = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.1
        sub_bass = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.1
        
        out_left, out_right = mixer.mix_and_limit(
            left, right, isochronic, harmonic, pad, noise, sub_bass
        )
        
        assert out_left.shape == left.shape
        assert out_right.shape == right.shape

    def test_mix_with_isochronic(self):
        """Test mixing with isochronic layer."""
        mixer = AudioMixer()
        left = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.5
        right = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.5
        isochronic = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.3
        
        out_left, out_right = mixer.mix_and_limit(left, right, isochronic=isochronic)
        
        assert out_left.shape == left.shape
        assert out_right.shape == right.shape

    def test_mix_with_harmonic(self):
        """Test mixing with harmonic layer."""
        mixer = AudioMixer()
        left = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.5
        right = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.5
        harmonic = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.3
        
        out_left, out_right = mixer.mix_and_limit(left, right, harmonic=harmonic)
        
        assert out_left.shape == left.shape
        assert out_right.shape == right.shape

    def test_mix_with_pad(self):
        """Test mixing with pad layer."""
        mixer = AudioMixer()
        left = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.5
        right = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.5
        pad = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.3
        
        out_left, out_right = mixer.mix_and_limit(left, right, pad=pad)
        
        assert out_left.shape == left.shape
        assert out_right.shape == right.shape

    def test_mix_with_noise(self):
        """Test mixing with noise layer."""
        mixer = AudioMixer()
        left = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.5
        right = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.5
        noise = np.random.randn(1000) * 0.1
        
        out_left, out_right = mixer.mix_and_limit(left, right, noise=noise)
        
        assert out_left.shape == left.shape
        assert out_right.shape == right.shape

    def test_mix_with_sub_bass(self):
        """Test mixing with sub-bass layer."""
        mixer = AudioMixer()
        left = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.5
        right = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.5
        sub_bass = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.2
        
        out_left, out_right = mixer.mix_and_limit(left, right, sub_bass=sub_bass)
        
        assert out_left.shape == left.shape
        assert out_right.shape == right.shape

    def test_sidechain_effect(self):
        """Test sidechain effect with sub-bass."""
        mixer = AudioMixer()
        left = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.5
        right = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.5
        pad = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.5
        # Create a loud sub-bass to trigger sidechain
        sub_bass = np.zeros(1000)
        sub_bass[100:200] = 0.5  # Loud hit
        
        out_left, out_right = mixer.mix_and_limit(left, right, pad=pad, sub_bass=sub_bass)
        
        assert out_left.shape == left.shape
        assert out_right.shape == right.shape

    def test_limiter_prevents_clipping(self):
        """Test that limiter prevents clipping."""
        mixer = AudioMixer()
        # Create loud signal
        left = np.ones(1000) * 0.5
        right = np.ones(1000) * 0.5
        
        out_left, out_right = mixer.mix_and_limit(left, right)
        
        # Output should be clipped
        assert np.all(np.abs(out_left) <= 1.0)
        assert np.all(np.abs(out_right) <= 1.0)

    def test_set_layer_gain(self):
        """Test setting layer gain."""
        mixer = AudioMixer()
        mixer.set_layer_gain("binaural", 0.8)
        assert mixer.binaural_gain == 0.8

    def test_set_layer_gain_clamping(self):
        """Test that layer gain is clamped."""
        mixer = AudioMixer()
        mixer.set_layer_gain("binaural", 5.0)
        assert mixer.binaural_gain == 2.0
        
        mixer.set_layer_gain("binaural", -1.0)
        assert mixer.binaural_gain == 0.0

    def test_set_all_layer_gains(self):
        """Test setting all layer gains."""
        mixer = AudioMixer()
        gains = {
            "binaural": 1.0,
            "isochronic": 0.6,
            "harmonic": 0.4,
            "pad": 0.3,
            "noise": 0.2,
            "sub_bass": 0.1,
        }
        for layer, gain in gains.items():
            mixer.set_layer_gain(layer, gain)
            assert getattr(mixer, f"{layer}_gain") == gain

    def test_invalid_layer_gain(self):
        """Test setting gain for invalid layer."""
        mixer = AudioMixer()
        mixer.set_layer_gain("invalid", 0.5)
        # Should not raise error

    def test_output_is_float32(self):
        """Test that output is always float32."""
        mixer = AudioMixer()
        left = np.sin(np.linspace(0, 2*np.pi, 1000)).astype(np.float64)
        right = np.sin(np.linspace(0, 2*np.pi, 1000)).astype(np.float64)
        
        out_left, out_right = mixer.mix_and_limit(left, right)
        
        assert out_left.dtype == np.float32
        assert out_right.dtype == np.float32

    def test_quiet_signal_preservation(self):
        """Test that quiet signals are mostly preserved."""
        mixer = AudioMixer()
        left = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.1
        right = np.sin(np.linspace(0, 2*np.pi, 1000)) * 0.1
        
        out_left, out_right = mixer.mix_and_limit(left, right)
        
        # Quiet signal should be mostly preserved (within limiter's effect)
        assert np.max(np.abs(out_left)) < 0.2
        assert np.max(np.abs(out_right)) < 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
