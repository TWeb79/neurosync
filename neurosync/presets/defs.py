"""
Preset Definitions
Author: Inventions4All - github:TWeb79

All preset definitions are imported from sessions/controller.py.
"""

from neurosync.sessions.controller import PRESETS, PresetCategory

# Categorized preset collections for convenience
SLEEP_PRESETS = {k: v for k, v in PRESETS.items() if v.category == PresetCategory.SLEEP}
FOCUS_PRESETS = {k: v for k, v in PRESETS.items() if v.category == PresetCategory.FOCUS}
MEDITATION_PRESETS = {k: v for k, v in PRESETS.items() if v.category == PresetCategory.MEDITATION}
CREATIVITY_PRESETS = {k: v for k, v in PRESETS.items() if v.category == PresetCategory.CREATIVITY}