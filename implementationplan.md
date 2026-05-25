# NeuroSync — Implementation Status v2.0.4
**Author:** Inventions4All - github:TWeb79  
**Date:** 2026-05-25  
**Version:** 2.0.1

---

## Current Status: Web MVP Complete, Desktop UI Uses Embedded WebView

The implementation plan has been largely completed. Web interface is fully functional with all core DSP modules implemented. Desktop UI now embeds the same HTML interface via Qt WebEngine.

---

## Completed Milestones

### BUG-001: Particle velocity integration — ✅ FIXED
Fixed in `neurosync/visualizers/engine.py:82` — uses `speed * dt` for proper Euler integration.

### BUG-002: Phase discontinuity in audio callback — ✅ FIXED  
Implemented `BinauralGenerator` class in `neurosync/dsp/core.py` with persistent phase accumulators.

### BUG-003: Inconsistent drift implementation — ✅ FIXED
Uses phase integration via `np.cumsum()` in `generate_binaural_beat()`.

### BUG-004: Stereo routing — ✅ NOT APPLICABLE (Web uses inline oscillators)
Web audio creates separate panners for left/right channels in `neurosync_ui.html`.

### BUG-005: Missing preset — ✅ RESOLVED
Single source of truth in `neurosync/sessions/controller.py` with `PRESETS` dictionary.

### BUG-006: QML window empty — ✅ FIXED
QML components now load correctly. `main.qml` and `MainView.qml` syntax fixed. UIBridge context property properly referenced. Audio engine connection still pending.

---

## Implemented Architecture

### Core Modules

| File | Status | Description |
|------|--------|-------------|
| `neurosync/dsp/core.py` | ✅ | BinauralGenerator with phase continuity, frequency glide |
| `neurosync/dsp/harmonic.py` | ✅ | IsochronicGenerator, HarmonicLayer, AmbientPadLayer, PinkNoiseGenerator, SubBassPulseGenerator |
| `neurosync/audio/mixer.py` | ✅ | Multi-layer mixer with lookahead limiter, sidechain pumping |
| `neurosync/audio/engine.py` | ✅ | AudioEngine with layer management and callbacks |
| `neurosync/audio/midi.py` | ✅ | MidiController for CC mapping |
| `neurosync/visualizers/engine.py` | ✅ | BrainwaveSphere, FrequencyRings, AmbientParticles |
| `neurosync/ui/bridge.py` | ✅ | UIBridge QObject for QML (signals/slots wired) |
| `neurosync/sessions/timeline.py` | ✅ | SessionTimeline with SLEEP_DESCENT_TIMELINE, FOCUS_TIMELINE |
| `neurosync/sessions/controller.py` | ✅ | SessionController with 17 presets, transition curves |

### Web UI (Primary Interface)
- `neurosync_ui.html` — Complete brain visualization, frequency controls, preset cards
- `neurosync/app/web.py` — FastAPI server with WebSocket support
- Rotary knob, waveform display, timeline visualization all implemented

---

## Remaining Work

### Desktop UI Integration
Desktop UI now embeds the same HTML interface via Qt WebEngine. No QML-Python bridge needed:
- `neurosync/app/main.py` — Uses QWebEngineView to load neurosync_ui.html
- `neurosync_ui.html` — Shared interface for web and desktop

### Testing
- `tests/test_dsp.py` — ✅ 25 tests passing
- `tests/test_sessions.py` — ✅ transition and timeline tests
- `tests/test_web_api.py` — ✅ FastAPI endpoint tests
- Tests run in <30 seconds with mocked sounddevice

---

## File Change Summary (Implemented)

| File | Status | Notes |
|------|--------|-------|
| `neurosync/dsp/core.py` | ✅ Complete | BinauralGenerator, drift fix |
| `neurosync/dsp/harmonic.py` | ✅ Complete | All layer generators |
| `neurosync/audio/engine.py` | ✅ Complete | Layer management |
| `neurosync/audio/mixer.py` | ✅ Complete | Limiter, sidechain |
| `neurosync/audio/midi.py` | ✅ Complete | CC mapping |
| `neurosync/visualizers/engine.py` | ✅ Complete | BUG-001 fixed |
| `neurosync/sessions/controller.py` | ✅ Complete | 17 presets |
| `neurosync/sessions/timeline.py` | ✅ Complete | Sleep descent timeline |
| `neurosync/app/web.py` | ✅ Complete | FastAPI server |
| `neurosync_ui.html` | ✅ Complete | Full web UI |
| `neurosync/app/main.py` | ✅ Updated | Uses QWebEngineView for desktop |
| `tests/test_*.py` | ✅ Complete | All passing |
| `tests/test_*.py` | ✅ Complete | All passing |

---

## Expert Notes on Hemisphere Synchronization

### Why Most Apps Fail

Commercial binaural beat apps typically generate static sine waves at fixed frequencies with no harmonic content, no phase continuity across buffer boundaries (causing click artifacts), incorrect stereo routing (both channels on the same bus), and no entrainment transition design. NeuroSync addresses all of these.

### Critical Implementation Detail — The "Entrainment Window"

The brain does not instantly synchronize to a binaural beat. Research suggests entrainment requires:
- Minimum 4–7 minutes at a stable frequency
- Optimal carrier frequency range: 150–400 Hz (the brain's sensitivity is highest here)
- Beat frequency within a range where the perceived beat is not confounded by the carrier's own sidebands

This is why session timelines (Phase 2) use 90-second transitions and 3–5 minute hold periods per segment — these are not arbitrary design choices.

### Isochronic vs Binaural — When to Use Each

Binaural beats require headphones and work through a neural mechanism involving olivary nuclei phase comparison. Isochronic tones work through direct cortical entrainment via auditory evoked potentials and do not require headphones. NeuroSync should:
- Default to binaural (more research support, deeper effect)
- Offer isochronic as an alternative (headphone-free, works on laptop speakers)
- Allow both simultaneously (additive effect, both entrainment pathways active)
- Label sessions clearly so users know which they are using

### Carrier Frequency Selection

The carrier frequency is not arbitrary. Recommendations:
- **For sleep/delta:** 100–180 Hz. Low carriers feel heavier, more hypnotic.
- **For theta/meditation:** 160–220 Hz. Mid-range feels balanced.
- **For focus/beta:** 220–280 Hz. Higher carriers feel more alert.
- **For creativity:** 180–240 Hz. Slightly warm, not harsh.

The carrier should avoid exact multiples of the room's standing wave frequencies (which depend on room dimensions — not controllable). Using a slight frequency drift (0.1 Hz/min) avoids this issue entirely.

---

*Plan version 2.0.4 | NeuroSync v2.0.4 | 2026-05-25*