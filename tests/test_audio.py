"""
Tests for Audio Engine
Author: Inventions4All - github:TWeb79
"""

import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from neurosync.audio.engine import AudioConfig, BrainwaveBand, AudioEngine


class TestAudioConfig:
    """Tests for audio configuration."""

    def test_default_config(self):
        """Test default audio configuration."""
        config = AudioConfig()
        assert config.sample_rate == 44100
        assert config.buffer_size == 1024
        assert config.channels == 2

    def test_custom_config(self):
        """Test custom audio configuration."""
        config = AudioConfig(sample_rate=48000, buffer_size=512)
        assert config.sample_rate == 48000
        assert config.buffer_size == 512

    def test_custom_dtype(self):
        """Test audio config with custom dtype."""
        config = AudioConfig(dtype="float64")
        assert config.dtype == "float64"


class TestBrainwaveBand:
    """Tests for brainwave band enum."""

    def test_delta_range(self):
        """Test delta frequency range."""
        assert BrainwaveBand.DELTA.value == (0.5, 4.0)

    def test_theta_range(self):
        """Test theta frequency range."""
        assert BrainwaveBand.THETA.value == (4.0, 8.0)

    def test_alpha_range(self):
        """Test alpha frequency range."""
        assert BrainwaveBand.ALPHA.value == (8.0, 12.0)

    def test_beta_range(self):
        """Test beta frequency range."""
        assert BrainwaveBand.BETA.value == (13.0, 30.0)

    def test_gamma_range(self):
        """Test gamma frequency range."""
        assert BrainwaveBand.GAMMA.value == (30.0, 80.0)


class TestAudioEngine:
    """Tests for audio engine."""

    def test_engine_initialization(self):
        """Test audio engine initialization."""
        config = AudioConfig()
        engine = AudioEngine(config)
        assert engine.config == config
        assert engine._stream is None
        assert engine._running is False
        assert engine._is_playing is False

    def test_engine_default_config(self):
        """Test engine with default config."""
        engine = AudioEngine()
        assert engine.config.sample_rate == 44100

    def test_set_callback(self):
        """Test setting audio callback."""
        engine = AudioEngine()
        callback = MagicMock()
        engine.set_callback(callback)
        assert engine._callback == callback

    def test_set_frequencies(self):
        """Test setting carrier and beat frequencies."""
        engine = AudioEngine()
        engine.set_frequencies(240.0, 12.0)
        assert engine._carrier_freq == 240.0
        assert engine._beat_freq == 12.0

    def test_set_volume(self):
        """Test setting volume."""
        engine = AudioEngine()
        engine.set_volume(0.8)
        assert engine._volume == 0.8

    def test_set_volume_clamping_high(self):
        """Test volume clamping at high end."""
        engine = AudioEngine()
        engine.set_volume(2.0)
        assert engine._volume == 1.0

    def test_set_volume_clamping_low(self):
        """Test volume clamping at low end."""
        engine = AudioEngine()
        engine.set_volume(-0.5)
        assert engine._volume == 0.0

    def test_set_layer_enabled(self):
        """Test enabling/disabling audio layers."""
        engine = AudioEngine()
        engine.set_layer_enabled("binaural", False)
        assert engine._layers_enabled["binaural"] is False
        engine.set_layer_enabled("isochronic", True)
        assert engine._layers_enabled["isochronic"] is True

    def test_all_layers_controllable(self):
        """Test that all layers can be controlled."""
        engine = AudioEngine()
        layers = ["binaural", "isochronic", "harmonic", "pad", "noise", "sub_bass"]
        for layer in layers:
            engine.set_layer_enabled(layer, False)
            assert engine._layers_enabled[layer] is False

    def test_invalid_layer(self):
        """Test setting invalid layer."""
        engine = AudioEngine()
        engine.set_layer_enabled("invalid_layer", True)
        # Should not raise error, just not set anything

    def test_dsp_components_initialized(self):
        """Test that DSP components are initialized."""
        engine = AudioEngine()
        assert engine._binaural_generator is not None
        assert engine._isochronic_generator is not None
        assert engine._harmonic_layer is not None
        assert engine._ambient_pad_layer is not None
        assert engine._pink_noise_generator is not None
        assert engine._sub_bass_generator is not None
        assert engine._mixer is not None

    @patch('neurosync.audio.engine.sd.OutputStream')
    def test_start_stream(self, mock_stream_class):
        """Test starting audio stream."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        engine = AudioEngine()
        engine.start()
        
        assert engine._stream is not None
        assert engine._running is True
        assert engine._is_playing is True
        mock_stream.start.assert_called_once()

    @patch('neurosync.audio.engine.sd.OutputStream')
    def test_start_already_running(self, mock_stream_class):
        """Test starting stream when already running."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        engine = AudioEngine()
        engine.start()
        engine.start()  # Should not create duplicate stream
        
        assert mock_stream_class.call_count == 1

    @patch('neurosync.audio.engine.sd.OutputStream')
    def test_stop_stream(self, mock_stream_class):
        """Test stopping audio stream."""
        mock_stream = MagicMock()
        mock_stream_class.return_value = mock_stream
        
        engine = AudioEngine()
        engine.start()
        engine.stop()
        
        assert engine._stream is None
        assert engine._running is False
        assert engine._is_playing is False
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()

    @patch('neurosync.audio.engine.sd.OutputStream')
    def test_stop_when_not_running(self, mock_stream_class):
        """Test stopping when not running."""
        engine = AudioEngine()
        engine.stop()  # Should not raise error
        assert engine._stream is None

    def test_set_frequencies_invalid_carrier(self):
        """Test setting frequencies with invalid carrier."""
        engine = AudioEngine()
        with pytest.raises(ValueError, match="Carrier frequency must be positive"):
            engine.set_frequencies(-10.0, 10.0)

    def test_set_frequencies_invalid_carrier_range(self):
        """Test setting frequencies with carrier out of range."""
        engine = AudioEngine()
        with pytest.raises(ValueError, match="Carrier frequency exceeds safe range"):
            engine.set_frequencies(25000.0, 10.0)

    def test_set_frequencies_invalid_beat(self):
        """Test setting frequencies with invalid beat."""
        engine = AudioEngine()
        with pytest.raises(ValueError, match="Beat frequency must be positive"):
            engine.set_frequencies(220.0, -5.0)

    def test_set_frequencies_invalid_beat_range(self):
        """Test setting frequencies with beat out of range."""
        engine = AudioEngine()
        with pytest.raises(ValueError, match="Beat frequency exceeds safe range"):
            engine.set_frequencies(220.0, 150.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])