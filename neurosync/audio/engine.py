"""
Audio Engine - Realtime Audio Playback
Author: Inventions4All - github:TWeb79
"""

import logging
import numpy as np
import sounddevice as sd
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional
from neurosync.audio.mixer import AudioMixer
from neurosync.dsp.core import BinauralGenerator
from neurosync.dsp.harmonic import IsochronicGenerator, HarmonicLayer, AmbientPadLayer, PinkNoiseGenerator, SubBassPulseGenerator

logger = logging.getLogger(__name__)


class BrainwaveBand(Enum):
    """Brainwave frequency bands."""

    DELTA = (0.5, 4.0)
    THETA = (4.0, 8.0)
    ALPHA = (8.0, 12.0)
    BETA = (13.0, 30.0)
    GAMMA = (30.0, 80.0)


@dataclass
class AudioConfig:
    """Audio configuration settings."""

    sample_rate: int = 44100
    buffer_size: int = 1024
    channels: int = 2
    dtype: str = "float32"


class AudioEngine:
    """Realtime audio playback engine for binaural beats."""

    def __init__(self, config: AudioConfig | None = None):
        """Initialize audio engine.

        Args:
            config: Audio configuration (uses defaults if None)
        """
        self.config = config or AudioConfig()
        self._stream: sd.OutputStream | None = None
        self._callback: Optional[Callable[[int], tuple[np.ndarray, np.ndarray]]] = None
        self._running = False
        
        # Initialize DSP components
        self._binaural_generator = BinauralGenerator(self.config.sample_rate)
        self._isochronic_generator = IsochronicGenerator(self.config.sample_rate)
        self._harmonic_layer = HarmonicLayer(self.config.sample_rate)
        self._ambient_pad_layer = AmbientPadLayer(self.config.sample_rate)
        self._pink_noise_generator = PinkNoiseGenerator(self.config.sample_rate)
        self._sub_bass_generator = SubBassPulseGenerator(self.config.sample_rate)
        self._mixer = AudioMixer(self.config.sample_rate)
        
        # Current parameters
        self._carrier_freq = 220.0
        self._beat_freq = 10.0
        self._volume = 0.5
        self._is_playing = False
        
        # Layer states
        self._layers_enabled = {
            'binaural': True,
            'isochronic': False,
            'harmonic': True,
            'pad': True,
            'noise': True,
            'sub_bass': False
        }

    def set_callback(self, callback: Callable[[int], tuple[np.ndarray, np.ndarray]]) -> None:
        """Set the audio callback function.

        Args:
            callback: Function that returns (left, right) numpy arrays
        """
        self._callback = callback

    def set_frequencies(self, carrier_freq: float, beat_freq: float) -> None:
        """Set carrier and beat frequencies.

        Args:
            carrier_freq: Carrier frequency in Hz (must be > 0)
            beat_freq: Beat frequency in Hz (must be > 0)
            
        Raises:
            ValueError: If frequencies are not positive or exceed safe ranges
        """
        # Validate carrier frequency
        if carrier_freq <= 0:
            raise ValueError(f"Carrier frequency must be positive, got {carrier_freq}")
        if carrier_freq > 20000:
            raise ValueError(f"Carrier frequency exceeds safe range (>20kHz): {carrier_freq}")
        
        # Validate beat frequency
        if beat_freq <= 0:
            raise ValueError(f"Beat frequency must be positive, got {beat_freq}")
        if beat_freq > 100:
            raise ValueError(f"Beat frequency exceeds safe range (>100Hz): {beat_freq}")
        
        self._carrier_freq = carrier_freq
        self._beat_freq = beat_freq
        self._binaural_generator.set_target_carrier(carrier_freq)
        self._binaural_generator.set_target_beat(beat_freq)

    def set_volume(self, volume: float) -> None:
        """Set playback volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self._volume = max(0.0, min(1.0, volume))

    def set_layer_enabled(self, layer: str, enabled: bool) -> None:
        """Enable or disable an audio layer.

        Args:
            layer: Layer name (binaural, isochronic, harmonic, pad, noise, sub_bass)
            enabled: Whether to enable the layer
        """
        if layer in self._layers_enabled:
            self._layers_enabled[layer] = enabled

    def start(self) -> None:
        """Start audio playback."""
        if self._stream is not None:
            return

        self._stream = sd.OutputStream(
            samplerate=self.config.sample_rate,
            blocksize=self.config.buffer_size,
            channels=self.config.channels,
            dtype=self.config.dtype,
            callback=self._audio_callback,
        )
        self._stream.start()
        self._running = True
        self._is_playing = True

    def stop(self) -> None:
        """Stop audio playback."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self._running = False
        self._is_playing = False

    def _audio_callback(self, outdata, frames, time, status):
        """Internal callback for audio stream."""
        if status:
            logger.warning(f"Audio stream status: {status}")

        if self._is_playing:
            # Generate audio from all layers
            # Generate binaural beat
            binaural_left, binaural_right = self._binaural_generator.generate_frame(
                self._carrier_freq, self._beat_freq, frames
            )
            
            # Generate isochronic tone if enabled
            isochronic = None
            if self._layers_enabled['isochronic']:
                isochronic = self._isochronic_generator.generate(
                    self._carrier_freq, self._beat_freq, frames / self.config.sample_rate
                )
            
            # Generate harmonic stack if enabled
            harmonic = None
            if self._layers_enabled['harmonic']:
                harmonic = self._harmonic_layer.generate(
                    self._carrier_freq, frames / self.config.sample_rate
                )
            
            # Generate ambient pad if enabled
            pad = None
            if self._layers_enabled['pad']:
                pad = self._ambient_pad_layer.generate(
                    frames / self.config.sample_rate, self._carrier_freq * 0.5
                )
            
            # Generate noise if enabled
            noise = None
            if self._layers_enabled['noise']:
                noise = self._pink_noise_generator.generate(
                    frames / self.config.sample_rate
                )
            
            # Generate sub-bass if enabled
            sub_bass = None
            if self._layers_enabled['sub_bass']:
                sub_bass = self._sub_bass_generator.generate(
                    frames / self.config.sample_rate
                )
            
            # Mix all layers
            left, right = self._mixer.mix_and_limit(
                binaural_left, binaural_right,
                isochronic, harmonic, pad, noise, sub_bass
            )
            
            # Apply volume
            left = left * self._volume
            right = right * self._volume
            
            # Output to stereo
            outdata[:, 0] = left.astype(np.float32)
            outdata[:, 1] = right.astype(np.float32)
        else:
            # Silence when not playing
            outdata.fill(0)

    @property
    def is_running(self) -> bool:
        """Check if audio is currently playing."""
        return self._running