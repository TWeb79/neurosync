"""
Session Controller - Session Management and Transitions
Author: Inventions4All - github:TWeb79
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class PresetCategory(Enum):
    """Session preset categories."""

    SLEEP = "sleep"
    FOCUS = "focus"
    MEDITATION = "meditation"
    CREATIVITY = "creativity"


@dataclass
class Preset:
    """Session preset configuration."""

    name: str
    category: PresetCategory
    beat_frequency: float
    carrier_frequency: float = 220.0
    duration: float = 60.0
    drift_rate: float = 0.0


# Preset definitions
PRESETS: dict[str, Preset] = {
    # Sleep presets
    "deep_sleep": Preset("Deep Sleep", PresetCategory.SLEEP, 2.0, 180.0),
    "rem_sleep": Preset("REM Sleep", PresetCategory.SLEEP, 4.0, 160.0),
    "power_nap": Preset("Power Nap", PresetCategory.SLEEP, 6.0, 200.0),
    "sleep_descent": Preset("Sleep Descent", PresetCategory.SLEEP, 10.0, 180.0),
    # Focus presets
    "coding_flow": Preset("Coding Flow", PresetCategory.FOCUS, 14.0, 220.0),
    "deep_work": Preset("Deep Work", PresetCategory.FOCUS, 18.0, 240.0),
    "adhd_focus": Preset("ADHD Focus", PresetCategory.FOCUS, 12.0, 200.0),
    "study_session": Preset("Study Session", PresetCategory.FOCUS, 16.0, 210.0),
    # Meditation presets
    "zen_meditation": Preset("Zen Meditation", PresetCategory.MEDITATION, 7.0),
    "breathwork": Preset("Breathwork", PresetCategory.MEDITATION, 6.0),
    "chakra_flow": Preset("Chakra Flow", PresetCategory.MEDITATION, 8.0),
    # Creativity presets
    "creative_flow": Preset("Creative Flow", PresetCategory.CREATIVITY, 7.0),
    "writing_session": Preset("Writing Session", PresetCategory.CREATIVITY, 8.0),
    "visual_design": Preset("Visual Design", PresetCategory.CREATIVITY, 10.0),
}


class SessionController:
    """Manages session state and transitions."""

    def __init__(self):
        """Initialize session controller."""
        self.current_preset: Preset | None = None
        self.state_changed: Callable[[str], None] | None = None
        self._transition_progress = 0.0

    def load_preset(self, preset_name: str) -> Preset:
        """Load a preset by name.

        Args:
            preset_name: Name of the preset to load

        Returns:
            The loaded Preset object

        Raises:
            KeyError: If preset doesn't exist
        """
        preset = PRESETS[preset_name]
        self.current_preset = preset
        if self.state_changed:
            self.state_changed(f"Loaded: {preset.name}")
        return preset

    def get_transition_curve(
        self,
        start_freq: float,
        target_freq: float,
        progress: float,
    ) -> float:
        """Calculate frequency at transition progress.

        Uses smooth easing for natural transitions.

        Args:
            start_freq: Starting frequency
            target_freq: Target frequency
            progress: Progress 0.0 to 1.0

        Returns:
            Interpolated frequency
        """
        eased = 1 - (1 - progress) ** 2
        return start_freq + (target_freq - start_freq) * eased