# NeuroSync Architecture

## System Structure

```
+---------------------------+
|       QML UI Layer        |
|  (PySide6 + QtQuick)      |
+---------------------------+
             |
             v
+---------------------------+
|    Session Controller     |
|   (sessions/controller)   |
+---------------------------+
             |
             v
+---------------------------+
|    Audio Orchestration    |
|     (audio/engine)        |
+---------------------------+
             |
             v
+---------------------------+
|    DSP Engine / Core      |
|     (dsp/core)            |
+---------------------------+
             |
             v
+---------------------------+
|   Audio Driver Layer      |
| (sounddevice + PortAudio) |
+---------------------------+
```

## Module Responsibilities

| Module | Responsibility |
| ------ | -------------- |
| `app/` | Application bootstrap and entry point |
| `ui/` | QML interface, themes, visual components |
| `audio/` | Audio playback, streaming, mixing |
| `dsp/` | DSP core: sine generation, binaural synthesis, filters |
| `sessions/` | Session automation, presets, transitions |
| `visualizers/` | Realtime visual effects, particles, FFT |

## Data Flow

1. User selects preset from UI
2. SessionController loads preset configuration
3. AudioEngine requests buffer from DSP core
4. DSP generates binaural beats with current parameters
5. Audio is streamed via sounddevice to output device
6. Visualizer receives frequency/amplitude data for rendering

## External Dependencies

- **numpy/scipy**: Numerical computation, FFT
- **sounddevice**: Realtime audio I/O
- **PySide6**: Desktop UI framework
- **PortAudio**: Cross-platform audio library