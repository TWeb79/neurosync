"""
Preset Definitions
Author: Inventions4All - github:TWeb79
"""

from neurosync.sessions.controller import Preset, PresetCategory

# Sleep Presets
SLEEP_PRESETS = {
    "deep_sleep": Preset("Deep Sleep", PresetCategory.SLEEP, 2.0, carrier_frequency=180.0),
    "rem_sleep": Preset("REM Sleep", PresetCategory.SLEEP, 4.0, carrier_frequency=160.0),
    "power_nap": Preset("Power Nap", PresetCategory.SLEEP, 6.0, carrier_frequency=200.0),
    "sleep_descent": Preset("Sleep Descent", PresetCategory.SLEEP, 10.0, carrier_frequency=180.0),
}

# Focus Presets
FOCUS_PRESETS = {
    "coding_flow": Preset("Coding Flow", PresetCategory.FOCUS, 14.0, carrier_frequency=220.0),
    "deep_work": Preset("Deep Work", PresetCategory.FOCUS, 18.0, carrier_frequency=240.0),
    "adhd_focus": Preset("ADHD Focus", PresetCategory.FOCUS, 12.0, carrier_frequency=200.0),
    "study_session": Preset("Study Session", PresetCategory.FOCUS, 16.0, carrier_frequency=210.0),
}

# Meditation Presets
MEDITATION_PRESETS = {
    "zen_meditation": Preset("Zen Meditation", PresetCategory.MEDITATION, 7.0),
    "breathwork": Preset("Breathwork", PresetCategory.MEDITATION, 6.0),
    "chakra_flow": Preset("Chakra Flow", PresetCategory.MEDITATION, 8.0),
    "emotional_release": Preset("Emotional Release", PresetCategory.MEDITATION, 5.0),
}

# Creativity Presets
CREATIVITY_PRESETS = {
    "creative_flow": Preset("Creative Flow", PresetCategory.CREATIVITY, 7.0),
    "writing_session": Preset("Writing Session", PresetCategory.CREATIVITY, 8.0),
    "visual_design": Preset("Visual Design", PresetCategory.CREATIVITY, 10.0),
    "musical_creativity": Preset("Musical Creativity", PresetCategory.CREATIVITY, 6.0),
}