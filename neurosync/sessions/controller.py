"""
Session Controller - Session Management and Transitions
Author: Inventions4All - github:TWeb79
"""

import numpy as np
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
    description: str = ""
    brainwave_band: str = ""
    color_theme: str = "cyan"
    recommended_duration: float = 1800.0
    headphones_required: bool = True


def _get_band(frequency: float) -> str:
    if frequency < 4.0:
        return "Delta"
    elif frequency < 8.0:
        return "Theta"
    elif frequency < 13.0:
        return "Alpha"
    elif frequency < 30.0:
        return "Beta"
    return "Gamma"


PRESETS: dict[str, Preset] = {
    "deep_sleep": Preset(
        "Deep Sleep",
        PresetCategory.SLEEP,
        2.0,
        carrier_frequency=180.0,
        description="Deep delta waves for restorative sleep",
        brainwave_band="Delta",
        color_theme="indigo",
    ),
    "rem_sleep": Preset(
        "REM Sleep",
        PresetCategory.SLEEP,
        4.0,
        carrier_frequency=160.0,
        description="Theta waves for REM sleep cycles",
        brainwave_band="Theta",
        color_theme="violet",
    ),
    "power_nap": Preset(
        "Power Nap",
        PresetCategory.SLEEP,
        6.0,
        carrier_frequency=200.0,
        description="Quick theta boost for 20-minute nap",
        brainwave_band="Theta",
        color_theme="violet",
    ),
    "sleep_descent": Preset(
        "Sleep Descent",
        PresetCategory.SLEEP,
        16.0,
        carrier_frequency=240.0,
        duration=3600.0,
        description="Full 60-minute descent from beta to delta",
        brainwave_band="Beta",
        color_theme="cyan",
    ),
    "coding_flow": Preset(
        "Coding Flow",
        PresetCategory.FOCUS,
        14.0,
        carrier_frequency=220.0,
        description="Beta waves for sustained concentration",
        brainwave_band="Beta",
        color_theme="emerald",
    ),
    "deep_work": Preset(
        "Deep Work",
        PresetCategory.FOCUS,
        18.0,
        carrier_frequency=240.0,
        description="High beta for intense focus sessions",
        brainwave_band="Beta",
        color_theme="emerald",
    ),
    "adhd_focus": Preset(
        "ADHD Focus",
        PresetCategory.FOCUS,
        12.0,
        carrier_frequency=200.0,
        description="Alpha-beta bridge for attention regulation",
        brainwave_band="Alpha",
        color_theme="cyan",
    ),
    "study_session": Preset(
        "Study Session",
        PresetCategory.FOCUS,
        16.0,
        carrier_frequency=210.0,
        description="Steady beta for academic work",
        brainwave_band="Beta",
        color_theme="emerald",
    ),
    "zen_meditation": Preset(
        "Zen Meditation",
        PresetCategory.MEDITATION,
        7.0,
        carrier_frequency=200.0,
        description="Golden theta for deep meditation",
        brainwave_band="Theta",
        color_theme="violet",
    ),
    "breathwork": Preset(
        "Breathwork",
        PresetCategory.MEDITATION,
        6.0,
        carrier_frequency=180.0,
        description="Coherent breathing rhythm entrainment",
        brainwave_band="Theta",
        color_theme="violet",
    ),
    "chakra_flow": Preset(
        "Chakra Flow",
        PresetCategory.MEDITATION,
        8.0,
        carrier_frequency=220.0,
        description="Alpha waves for chakra alignment",
        brainwave_band="Alpha",
        color_theme="cyan",
    ),
    "creative_flow": Preset(
        "Creative Flow",
        PresetCategory.CREATIVITY,
        7.0,
        carrier_frequency=180.0,
        description="Theta-alpha blend for creative insight",
        brainwave_band="Theta",
        color_theme="amber",
    ),
    "writing_session": Preset(
        "Writing Session",
        PresetCategory.CREATIVITY,
        8.0,
        carrier_frequency=200.0,
        description="Alpha waves for fluid expression",
        brainwave_band="Alpha",
        color_theme="amber",
    ),
    "visual_design": Preset(
        "Visual Design",
        PresetCategory.CREATIVITY,
        10.0,
        carrier_frequency=220.0,
        description="Higher alpha for visual processing",
        brainwave_band="Alpha",
        color_theme="amber",
    ),
    # Schumann Resonance Carrier Modes
    "schumann_7hz": Preset(
        "Schumann 7.83Hz",
        PresetCategory.MEDITATION,
        7.83,
        carrier_frequency=136.1,  # Earth year frequency
        description="Schumann resonance fundamental with Earth year carrier",
        brainwave_band="Theta",
        color_theme="violet",
        headphones_required=True,
    ),
    "schumann_14hz": Preset(
        "Schumann 14.3Hz",
        PresetCategory.FOCUS,
        14.3,
        carrier_frequency=172.0,  # Earth day frequency
        description="Schumann resonance harmonic with Earth day carrier",
        brainwave_band="Beta",
        color_theme="emerald",
        headphones_required=True,
    ),
    "schumann_21hz": Preset(
        "Schumann 20.8Hz",
        PresetCategory.CREATIVITY,
        20.8,
        carrier_frequency=221.2,  # Popular healing frequency
        description="Schumann resonance harmonic with healing frequency carrier",
        brainwave_band="Beta",
        color_theme="amber",
        headphones_required=True,
    ),
}


class SessionController:
    """Manages session state and transitions."""

    def __init__(self):
        self.current_preset: Preset | None = None
        self.state_changed: Callable[[str], None] | None = None
        self._transition_progress = 0.0

    def load_preset(self, preset_name: str) -> Preset:
        """Load a session preset by name.

        Args:
            preset_name: Name of the preset to load

        Returns:
            The preset configuration

        Raises:
            KeyError: If preset_name is not found in PRESETS registry
        """
        if preset_name not in PRESETS:
            available = ", ".join(sorted(PRESETS.keys()))
            raise KeyError(f"Unknown preset '{preset_name}'. Available: {available}")
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

    def get_eased_value(
        self,
        start_val: float,
        end_val: float,
        progress: float,
        ease_type: str = "ease_in_out",
    ) -> float:
        """Apply easing function to transition.

        Args:
            start_val: Starting value
            end_val: Ending value
            progress: Progress 0.0 to 1.0
            ease_type: Easing type (linear, ease_in, ease_out, ease_in_out, exponential)

        Returns:
            Eased value
        """
        if ease_type == "linear":
            return start_val + (end_val - start_val) * progress
        elif ease_type == "ease_in":
            return start_val + (end_val - start_val) * progress**2
        elif ease_type == "ease_out":
            return start_val + (end_val - start_val) * (1 - (1 - progress) ** 2)
        elif ease_type == "exponential":
            return start_val + (end_val - start_val) * (np.exp(3 * progress) - 1) / (np.e**3 - 1)
        else:
            eased = 1 - (1 - progress) ** 3
            return start_val + (end_val - start_val) * eased