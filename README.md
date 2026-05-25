# NeuroSync - Adaptive Brainwave Audio Studio

**Version:** 2.0.3 (2026-05-25)  
**Author:** Inventions4All - github:TWeb79

A desktop audio application combining binaural beats, isochronic tones, and adaptive frequency entrainment with immersive visualizations.

## Status

**Phase Complete: Web MVP & Core DSP** — Fully functional web interface with brain visualization, multi-layer audio engine, and session timeline system. Desktop UI uses embedded web view (neurosync_ui.html).

## Features Implemented

- **Stateful BinauralGenerator** — Phase-continuous audio with 500ms exponential glide
- **Isochronic tones** — Speaker-compatible pulsing (no headphones required)
- **Harmonic stack** — Subtle overtones for reduced listening fatigue
- **Ambient pads** — Detuned oscillator background with LFO
- **Pink noise floor** — Voss algorithm implementation
- **Lookahead limiter** — Brickwall limiting at -3dBFS threshold
- **Web UI** — Brain visualization, frequency controls, preset cards
- **Session timelines** — Sleep descent (beta→delta) and focus (reset cycles)
- **MIDI controller support** — CC mapping for beat frequency and layers

## Purpose

NeuroSync creates premium neuro-acoustic experiences for:
- Meditation and sleep enhancement
- Focus and deep work sessions
- Creative flow states
- ADHD focus support

## Available Presets

| Category | Presets | Beat Range |
|----------|---------|------------|
| Sleep | Deep Sleep, REM Sleep, Power Nap, Sleep Descent | 1.5–6 Hz |
| Focus | Coding Flow, Deep Work, ADHD Focus, Study Session | 12–18 Hz |
| Meditation | Zen Meditation, Breathwork, Chakra Flow | 6–8 Hz |
| Creativity | Creative Flow, Writing Session, Visual Design | 7–10 Hz |
| Schumann | 7.83Hz, 14.3Hz, 20.8Hz | 7.83–20.8 Hz |

## Port Allocation (Project 45)

| Port | Service | Description |
| ---- | ------- | ----------- |
| 8045 | Web Dashboard | PySide6/QML UI |
| 8145 | API (reserved) | Future FastAPI service |
| 8245 | Database | PostgreSQL |
| 6379 | Cache | Redis |

## Dependencies

```bash
pip install -r requirements.txt
```

Required:
- Python 3.12+
- numpy, scipy (numerical DSP)
- sounddevice, soundfile (audio I/O)
- pedalboard (effects)
- PySide6 (UI)

## Installation

```bash
# Clone and install
git clone https://github.com/TWeb79/neurosync.git
cd 45-neurosync
pip install -e .
```

## Usage

```bash
# Run the web interface (default)
python -m neurosync.app.web
# Open http://localhost:8045 in your browser

# Run desktop application (embedded web UI)
python -m neurosync.app.main
```

## Project Structure

```
neurosync/
├── app/           # Application entry points (main.py, web.py)
├── audio/         # AudioEngine, AudioMixer, MidiController
├── dsp/           # BinauralGenerator, IsochronicGenerator, HarmonicLayer
├── sessions/      # SessionController, SessionTimeline
├── visualizers/   # BrainwaveSphere, FrequencyRings, AmbientParticles
├── presets/       # Preset definitions
├── tests/         # Test suite
└── neurosync_ui.html  # Standalone web interface (shared with desktop)
```

## Testing

```bash
pytest tests/
```