"""
Audio Mixer - Multi-layer audio mixing with limiter
Author: Inventions4All - github:TWeb79
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class LayerConfig:
    """Configuration for an audio layer."""

    enabled: bool = True
    gain: float = 1.0


class AudioMixer:
    """Multi-layer audio mixer for binaural beats, isochronic, and ambient layers."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.binaural_gain = 1.0
        self.isochronic_gain = 0.5
        self.harmonic_gain = 0.3
        self.pad_gain = 0.2
        self.noise_gain = 0.1
        self.sub_bass_gain = 0.08
        self._limiter_lookahead = 220
        self._limiter_buffer = np.zeros(self._limiter_lookahead)
        self._sidechain_reduction = 1.0
        self._sidechain_attack_time = 0.01  # 10ms
        self._sidechain_release_time = 0.1   # 100ms
        self._sidechain_attack_coeff = np.exp(-1.0 / (self._sidechain_attack_time * sample_rate))
        self._sidechain_release_coeff = np.exp(-1.0 / (self._sidechain_release_time * sample_rate))

    def mix_and_limit(
        self,
        binaural_left: np.ndarray,
        binaural_right: np.ndarray,
        isochronic: np.ndarray | None = None,
        harmonic: np.ndarray | None = None,
        pad: np.ndarray | None = None,
        noise: np.ndarray | None = None,
        sub_bass: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Mix all layers and apply lookahead limiter.

        Args:
            binaural_left: Left channel binaural signal
            binaural_right: Right channel binaural signal
            isochronic: Mono isochronic signal (centered)
            harmonic: Mono harmonic stack (centered)
            pad: Mono ambient pad (centered)
            noise: Mono noise floor (centered)
            sub_bass: Mono sub-bass signal (centered)

        Returns:
            Tuple of (left, right) mixed signals
        """
        left = binaural_left * self.binaural_gain
        right = binaural_right * self.binaural_gain

        if isochronic is not None:
            mono = isochronic * self.isochronic_gain
            left += mono * 0.5
            right += mono * 0.5

        if harmonic is not None:
            mono = harmonic * self.harmonic_gain
            left += mono * 0.5
            right += mono * 0.5

        if pad is not None:
            # Apply sidechain effect from sub-bass
            if sub_bass is not None:
                # Simple sidechain: reduce pad gain when sub-bass hits
                abs_sub_bass = np.abs(sub_bass)
                threshold = 0.1
                reduction = np.ones_like(abs_sub_bass)
                mask = abs_sub_bass > threshold
                if np.any(mask):
                    reduction[mask] = 0.3  # Reduce to 30% when kick hits
                    # Smooth the reduction
                    for i in range(1, len(reduction)):
                        if reduction[i] < reduction[i-1]:
                            reduction[i] = reduction[i-1] * self._sidechain_attack_coeff + reduction[i] * (1 - self._sidechain_attack_coeff)
                        else:
                            reduction[i] = reduction[i-1] * self._sidechain_release_coeff + reduction[i] * (1 - self._sidechain_release_coeff)
                mono = pad * self.pad_gain * reduction
            else:
                mono = pad * self.pad_gain
            left += mono * 0.5
            right += mono * 0.5

        if noise is not None:
            mono = noise * self.noise_gain
            left += mono
            right += mono

        if sub_bass is not None:
            mono = sub_bass * self.sub_bass_gain
            left += mono
            right += mono

        left = self._limiter(left)
        right = self._limiter(right)

        return left.astype(np.float32), right.astype(np.float32)

    def _limiter(self, signal: np.ndarray) -> np.ndarray:
        """Apply lookahead brickwall limiter.

        Args:
            signal: Input signal

        Returns:
            Limited signal
        """
        abs_signal = np.abs(signal)
        threshold = 10 ** (-3.0 / 20)
        gain = np.ones_like(signal)
        over = abs_signal > threshold
        if np.any(over):
            gain[over] = threshold / abs_signal[over]
            smooth_gain = np.minimum.accumulate(gain[::-1])[::-1]
            signal = signal * smooth_gain
        return signal * 0.95

    def set_layer_gain(self, layer: str, gain: float) -> None:
        """Set gain for a specific layer.

        Args:
            layer: Layer name (binaural, isochronic, harmonic, pad, noise, sub_bass)
            gain: Gain value (0.0 to 2.0)
        """
        if hasattr(self, f"{layer}_gain"):
            setattr(self, f"{layer}_gain", np.clip(gain, 0.0, 2.0))