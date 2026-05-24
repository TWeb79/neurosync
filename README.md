# NeuroSync - Adaptive Brainwave Audio Studio

**Version:** 0.1.0 (2026-05-24)  
**Author:** Inventions4All - github:TWeb79

A high-end desktop audio application combining binaural beats, isochronic tones, and adaptive frequency entrainment with immersive visualizations.

## Purpose

NeuroSync creates premium neuro-acoustic experiences for:
- Meditation and sleep enhancement
- Focus and deep work sessions
- Creative flow states
- ADHD focus support

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
git clone <repo-url>
cd 45-neurosync
pip install -e .
```

## Usage

```bash
# Run the application
python -m neurosync.app.main
```

## Docker

```bash
# Build and run
docker-compose up --build
```

## Project Structure

```
neurosync/
├── app/           # Application bootstrap
├── audio/         # Audio playback engine
├── dsp/           # Core signal processing
├── sessions/      # Session management
├── visualizers/   # Realtime visuals
├── ui/qml/        # QML interface
├── presets/       # Session presets
├── tests/         # Test suite
└── config/        # Configuration
```

## Testing

```bash
pytest tests/
```