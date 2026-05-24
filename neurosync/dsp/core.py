"""
DSP Core - Signal Generation for Binaural Beats
Author: Inventions4All - github:TWeb79
"""

import numpy as np


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

    left = carrier_freq
    right = carrier_freq + beat_freq

    if drift_rate != 0:
        carrier_drift = carrier_freq + drift_rate * t
        left = carrier_drift
        right = carrier_drift + beat_freq

    left_channel = np.sin(2 * np.pi * left * t)
    right_channel = np.sin(2 * np.pi * right * t)

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