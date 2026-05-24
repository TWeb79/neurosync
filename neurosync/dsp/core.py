"""
DSP Core - Signal Generation for Binaural Beats
Author: Inventions4All - github:TWeb79
"""

import numpy as np


class BinauralGenerator:
    """Stateful binaural beat generator with phase continuity."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self._phase_left = 0.0
        self._phase_right = 0.0
        self._carrier_current = 220.0
        self._carrier_target = 220.0
        self._beat_current = 10.0
        self._beat_target = 10.0
        self._glide_coeff = 1 - np.exp(-1 / (0.1 * sample_rate))

    def set_target_carrier(self, freq: float) -> None:
        self._carrier_target = freq

    def set_target_beat(self, freq: float) -> None:
        self._beat_target = freq

    def get_current_frequencies(self) -> dict:
        carrier = self._carrier_current
        beat = self._beat_current
        return {
            "carrier": carrier,
            "beat": beat,
            "left": carrier,
            "right": carrier + beat,
        }

    def _get_brainwave_band(self, beat_freq: float) -> str:
        if beat_freq < 4.0:
            return "Delta"
        elif beat_freq < 8.0:
            return "Theta"
        elif beat_freq < 13.0:
            return "Alpha"
        elif beat_freq < 30.0:
            return "Beta"
        else:
            return "Gamma"

    def generate_frame(
        self, carrier_freq: float, beat_freq: float, frames: int
    ) -> tuple[np.ndarray, np.ndarray]:
        """Generate audio frame with phase continuity."""
        left_freq = carrier_freq
        right_freq = carrier_freq + beat_freq
        phase_inc_left = 2 * np.pi * left_freq / self.sample_rate
        phase_inc_right = 2 * np.pi * right_freq / self.sample_rate
        t_left = self._phase_left + np.arange(frames) * phase_inc_left
        t_right = self._phase_right + np.arange(frames) * phase_inc_right
        self._phase_left = (self._phase_left + frames * phase_inc_left) % (2 * np.pi)
        self._phase_right = (self._phase_right + frames * phase_inc_right) % (2 * np.pi)
        left_channel = np.sin(t_left)
        right_channel = np.sin(t_right)
        self._carrier_current += (self._carrier_target - self._carrier_current) * self._glide_coeff
        self._beat_current += (self._beat_target - self._beat_current) * self._glide_coeff
        return left_channel, right_channel


def generate_sine_wave(frequency: float, duration: float, sample_rate: int) -> np.ndarray:
    """Generate a sine wave at the given frequency.

    Args:
        frequency: Frequency in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz

    Returns:
        Numpy array of sine wave samples
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return np.sin(2 * np.pi * frequency * t)


def interpolate_frequency(
    start_freq: float, end_freq: float, duration: float, sample_rate: int
) -> np.ndarray:
    """Generate smoothly interpolated frequency transition.

    Args:
        start_freq: Starting frequency in Hz
        end_freq: Ending frequency in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz

    Returns:
        Array of frequency values for each sample
    """
    num_samples = int(sample_rate * duration)
    return np.linspace(start_freq, end_freq, num_samples)


def calculate_binaural_frequencies(
    carrier_freq: float, beat_freq: float
) -> tuple[float, float]:
    """Calculate left and right channel frequencies for binaural beats.

    The binaural beat frequency is the difference between right and left.

    Args:
        carrier_freq: Base carrier frequency in Hz
        beat_freq: Desired beat frequency in Hz

    Returns:
        Tuple of (left_frequency, right_frequency)
    """
    left = carrier_freq
    right = carrier_freq + beat_freq
    return left, right


def generate_binaural_beat(
    carrier_freq: float,
    beat_freq: float,
    duration: float,
    sample_rate: int,
    drift_rate: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate stereo binaural beat with optional frequency drift.

    Args:
        carrier_freq: Base carrier frequency in Hz
        beat_freq: Beat frequency in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        drift_rate: Hz per second for carrier drift (default 0)

    Returns:
        Tuple of (left_channel, right_channel)
    """
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    if drift_rate != 0:
        left_instantaneous = carrier_freq + drift_rate * t
        right_instantaneous = carrier_freq + drift_rate * t + beat_freq
        left_phase = 2 * np.pi * np.cumsum(left_instantaneous) / sample_rate
        right_phase = 2 * np.pi * np.cumsum(right_instantaneous) / sample_rate
        left_channel = np.sin(left_phase)
        right_channel = np.sin(right_phase)
    else:
        left_channel = np.sin(2 * np.pi * carrier_freq * t)
        right_channel = np.sin(2 * np.pi * (carrier_freq + beat_freq) * t)

    return left_channel, right_channel


def apply_dB_limiter(
    signal: np.ndarray, threshold: float = -6.0, ratio: float = 4.0
) -> np.ndarray:
    """Apply soft limiting to prevent clipping.

    Args:
        signal: Input audio signal
        threshold: dB threshold for limiting
        ratio: Compression ratio

    Returns:
        Limited signal
    """
    threshold_linear = 10 ** (threshold / 20)
    abs_signal = np.abs(signal)
    over_threshold = abs_signal > threshold_linear

    if np.any(over_threshold):
        gain = np.ones_like(signal)
        gain[over_threshold] = (
            threshold_linear + (abs_signal[over_threshold] - threshold_linear) / ratio
        ) / abs_signal[over_threshold]
        signal = signal * gain

    return signal