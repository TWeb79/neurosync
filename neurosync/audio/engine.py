"""
Audio Engine - Realtime Audio Playback
Author: Inventions4All - github:TWeb79
"""

import numpy as np
import sounddevice as sd
from dataclasses import dataclass
from enum import Enum


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
        self._callback = None
        self._running = False

    def set_callback(self, callback):
        """Set the audio callback function.

        Args:
            callback: Function that returns (left, right) numpy arrays
        """
        self._callback = callback

    def start(self):
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

    def stop(self):
        """Stop audio playback."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self._running = False

    def _audio_callback(self, outdata, frames, time, status):
        """Internal callback for audio stream."""
        if status:
            print(f"Audio status: {status}")

        if self._callback is not None:
            left, right = self._callback(frames)
            outdata[:, 0] = left
            outdata[:, 1] = right
        else:
            outdata.fill(0)

    @property
    def is_running(self) -> bool:
        """Check if audio is currently playing."""
        return self._running