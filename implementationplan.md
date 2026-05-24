# NeuroSync Implementation Plan

## Phase 1: Foundation (Weeks 1-2)

### Week 1: Project Setup & DSP Core
- [ ] Initialize project structure (`neurosync/` directory with submodules)
- [ ] Set up `pyproject.toml` and `requirements.txt`
- [ ] Implement basic sine wave generator in `dsp/core.py`
- [ ] Implement binaural beat formula: `beat = right_freq - left_freq`
- [ ] Create stereo output handler
- [ ] Write unit tests for frequency calculations

### Week 2: Audio Engine & Safety
- [ ] Integrate `sounddevice` for realtime audio playback
- [ ] Implement audio callback system
- [ ] Add limiter/normalization for clipping prevention
- [ ] Add smooth frequency interpolation
- [ ] Create basic preset data structures

## Phase 2: Core Features (Weeks 3-4)

### Week 3: Session Engine
- [ ] Implement `SessionController` class
- [ ] Create transition curves (beta → alpha → theta → delta)
- [ ] Add easing functions for smooth transitions
- [ ] Build preset definitions for all 4 categories (Sleep, Focus, Meditation, Creativity)

### Week 4: Ambient Audio Layer
- [ ] Implement ambient pad generator
- [ ] Add filtered noise component
- [ ] Create drone/subsynth layer
- [ ] Add reverb tail processing
- [ ] Integrate `pedalboard` for DSP effects

## Phase 3: UI Prototype (Weeks 5-6)

### Week 5: PySide6 + QML Setup
- [ ] Bootstrap QML application window
- [ ] Create preset selection dashboard with animated cards
- [ ] Implement primary rotary frequency control knob
- [ ] Add display for current beat/carrier frequencies

### Week 6: Visualization & Polish
- [ ] Build stereo frequency visualizer
- [ ] Implement brainwave sphere animation
- [ ] Add frequency rings reactive to audio
- [ ] Create ambient particle system (basic)

## Phase 4: Advanced Features (Weeks 7-8)

### Week 7: Harmonic Layering & Drift
- [ ] Implement harmonic stack generation (saw harmonics)
- [ ] Add analog warmth/saturation
- [ ] Create dynamic frequency drift feature
- [ ] Optimize with numba JIT where needed

### Week 8: House Music Integration
- [ ] Add slow sidechain pulsing
- [ ] Implement lowpass rhythmic movement
- [ ] Create soft kick pulse generator
- [ ] Add atmospheric groove layer

## Phase 5: Production Ready (Weeks 9-10)

### Week 9: Docker & Testing
- [ ] Create Dockerfile with PortAudio dependencies
- [ ] Write docker-compose.yml (postgres, redis services)
- [ ] Add unit tests for DSP generation
- [ ] Add integration tests for playback

### Week 10: Packaging & Documentation
- [ ] Set up PyInstaller for desktop distribution
- [ ] Create GitHub Actions CI/CD pipeline
- [ ] Write user documentation
- [ ] Final polish and bug fixes

## Milestone Deliverables

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| M1: Core DSP | Week 2 | Working binaural beat generator with realtime playback |
| M2: Session Engine | Week 4 | Complete preset system with transitions |
| M3: UI Alpha | Week 6 | Interactive interface with visualization |
| M4: Audio Enhancement | Week 8 | Full ambient + house music layers |
| M5: Production | Week 10 | Packaged desktop app with tests |

## Technology Dependencies

**Required Libraries:**
- numpy, scipy (numerical DSP)
- sounddevice, soundfile (audio I/O)
- pedalboard (effects)
- PySide6 (UI)

**Optional (for performance):**
- numba (JIT compilation)
- pyqtgraph/moderngl (advanced visuals)

## Risk Mitigation

1. **Audio latency**: Use small buffer sizes, profile early
2. **CPU usage**: Vectorize with numpy, use numba for hot paths
3. **Docker audio**: Develop primarily on host, use Docker for backend services
4. **UI complexity**: Start with basic widgets, iterate on visuals