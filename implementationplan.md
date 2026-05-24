# NeuroSync — Updated Implementation Plan v2.0
**Author:** Inventions4All - github:TWeb79
**Date:** 2026-05-24
**Version:** 0.2.0

---

## Executive Summary

NeuroSync will be the definitive hemisphere synchronization application — combining neuroscience-grade binaural beat engineering, isochronic tones, and ambient generative music with a cinematic cyberpunk UI. This plan supersedes v1.0 and includes precise UI specifications, DSP architecture, bug fixes, and branding direction.

---

## Critical Bug Fixes (Pre-Implementation, Do Immediately)

### BUG-001: Particle velocity integration error — `neurosync/visualizers/engine.py`
```python
# WRONG (divides by dt, causing near-zero movement):
self.positions += self.velocities * speed / dt

# CORRECT (multiplies by dt for proper Euler integration):
self.positions += self.velocities * speed * dt
```

### BUG-002: Phase discontinuity in audio callback — `neurosync/audio/engine.py`
The DSP core generates binaural beats by segment (0..duration), but the callback receives frames independently. Each call to `generate_binaural_beat()` restarts phase at 0, causing audible clicks at buffer boundaries.

**Fix:** Introduce a persistent phase accumulator in the DSP core. The DSP generator must maintain `phase_left` and `phase_right` as class state, incrementing per sample, never resetting.

```python
# In dsp/core.py — add a stateful generator class alongside the pure functions:
class BinauralGenerator:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self._phase_left = 0.0
        self._phase_right = 0.0

    def generate_frame(self, carrier_freq: float, beat_freq: float, frames: int) -> tuple[np.ndarray, np.ndarray]:
        """Generate audio frame with phase continuity across callbacks."""
        left_freq = carrier_freq
        right_freq = carrier_freq + beat_freq
        phase_inc_left  = 2 * np.pi * left_freq  / self.sample_rate
        phase_inc_right = 2 * np.pi * right_freq / self.sample_rate
        t_left  = self._phase_left  + np.arange(frames) * phase_inc_left
        t_right = self._phase_right + np.arange(frames) * phase_inc_right
        self._phase_left  = (self._phase_left  + frames * phase_inc_left)  % (2 * np.pi)
        self._phase_right = (self._phase_right + frames * phase_inc_right) % (2 * np.pi)
        return np.sin(t_left), np.sin(t_right)
```

### BUG-003: Inconsistent drift implementation — `neurosync/dsp/core.py`
When `drift_rate != 0`, `right = carrier_drift + beat_freq` creates a numpy array, but `np.sin(2 * np.pi * right * t)` then computes element-wise frequency, which is NOT correct FM synthesis — it ignores phase accumulation. Replace with instantaneous phase integration:

```python
if drift_rate != 0:
    # Instantaneous frequency at each sample:
    left_instantaneous  = carrier_freq + drift_rate * t
    right_instantaneous = carrier_freq + drift_rate * t + beat_freq
    # Phase is the integral of instantaneous frequency:
    left_phase  = 2 * np.pi * np.cumsum(left_instantaneous)  / sample_rate
    right_phase = 2 * np.pi * np.cumsum(right_instantaneous) / sample_rate
    left_channel  = np.sin(left_phase)
    right_channel = np.sin(right_phase)
```

### BUG-004: Stereo routing not enforced in web.py
Web.py creates left and right oscillators but both connect to `audioCtx.destination` (stereo bus), mixing them together. For true binaural effect, each channel must be panned hard left/right:

```javascript
// After creating oscillators, add panners:
const leftPanner  = audioCtx.createStereoPanner();
const rightPanner = audioCtx.createStereoPanner();
leftPanner.pan.setValueAtTime(-1, audioCtx.currentTime);
rightPanner.pan.setValueAtTime( 1, audioCtx.currentTime);
leftOsc.connect(leftGain);   leftGain.connect(leftPanner);   leftPanner.connect(audioCtx.destination);
rightOsc.connect(rightGain); rightGain.connect(rightPanner); rightPanner.connect(audioCtx.destination);
```

### BUG-005: Missing preset — `neurosync/presets/defs.py` vs `sessions/controller.py`
Both files define `PRESETS` independently, causing drift. Remove the dictionary from `presets/defs.py` and import from `sessions/controller.py` as the single source of truth.

### BUG-006: QML window is empty — `neurosync/ui/qml/main.qml`
`main.qml` contains only an `ApplicationWindow` with no content. The entire QML UI needs to be built.

---

## Architecture Revision

### New Module: `neurosync/dsp/harmonic.py`
Harmonic layering, isochronic tone generation, ambient pad synthesis.

### New Module: `neurosync/dsp/isochronic.py`
Isochronic tones: amplitude-modulated carrier at the beat frequency (does not require headphones — works on speakers too).

### New Module: `neurosync/audio/mixer.py`
Multi-layer mixer combining binaural beat layer, isochronic layer, ambient pad layer, and noise layer with independent gain controls.

### New Module: `neurosync/ui/bridge.py`
PySide6 `QObject` subclass exposing Python DSP state to QML via `@Property`, `@Slot`, and `Signal`.

### Revised Data Flow
```
User selects preset in QML
        ↓
UIBridge.loadPreset(name)        [bridge.py]
        ↓
SessionController.load_preset()  [controller.py]
        ↓
AudioMixer.configure_layers()    [mixer.py]
        ↓ (callback thread, every 1024 samples ≈ 23ms at 44100 Hz)
BinauralGenerator.generate_frame()   [dsp/core.py]
HarmonicLayer.generate_frame()       [dsp/harmonic.py]
IsochronicLayer.generate_frame()     [dsp/isochronic.py]
AmbientPadLayer.generate_frame()     [dsp/harmonic.py]
        ↓
AudioMixer.mix_and_limit()       [mixer.py]
        ↓
sounddevice OutputStream callback
        ↓ (UI thread, every ~33ms / 30fps)
VisualizerEngine.update_from_fft()   [visualizers/engine.py]
UIBridge signals → QML update
```

---

## Phase 1 — DSP Foundation (Week 1–2)

### 1.1 Stateful BinauralGenerator (dsp/core.py)

Replace pure functions with `BinauralGenerator` class (see BUG-002 fix above). Add:
- `set_target_carrier(freq)` — sets interpolation target, engine glides there over 500ms
- `set_target_beat(freq)` — same for beat frequency
- `get_current_frequencies() -> dict` — returns `{carrier, beat, left, right, brainwave_band}` for UI display

Internal interpolation: use an exponential moving average with time constant 100ms (≈ 4410 samples). This gives a silky smooth frequency sweep without overshoot.

```python
# Exponential glide (per-sample in the hot path):
self._carrier_current += (self._carrier_target - self._carrier_current) * self._glide_coeff
# glide_coeff = 1 - exp(-1 / (0.1 * sample_rate))  # τ = 100ms
```

### 1.2 Isochronic Tones (dsp/isochronic.py)

Isochronic tones are distinct from binaural beats. They are a single carrier frequency amplitude-modulated at the beat frequency. Unlike binaural beats, they work on speakers.

```
Amplitude envelope: A(t) = sin(π × beat_freq × t)² clipped to [0,1]
Signal: s(t) = carrier_sine(t) × A(t)
```

The amplitude envelope uses squared sine for smooth on/off transitions (cosine rise/fall). The duty cycle should be adjustable (default 50%). Implement in `IsochronicGenerator` class with the same stateful phase approach.

**Key parameter:** Ramp time per cycle = duty_cycle / beat_freq. At 10 Hz and 50% duty cycle, each pulse is 50ms wide.

### 1.3 Harmonic Stack (dsp/harmonic.py)

Pure sine waves cause listener fatigue after ~10–15 minutes. The harmonic stack solves this by adding subtle overtones:

```python
class HarmonicLayer:
    """
    Generates psychoacoustically warm harmonic stack.
    
    Frequency structure (relative amplitudes):
        fundamental × 1.0 → amplitude 1.0   (100%)
        fundamental × 2.0 → amplitude 0.35  (35%)  — octave
        fundamental × 3.0 → amplitude 0.15  (15%)  — fifth
        fundamental × 4.0 → amplitude 0.08  (8%)   — second octave
        fundamental × 5.0 → amplitude 0.04  (4%)   — major third
    
    All harmonics are sine waves for a clean, non-fatiguing timbre.
    Apply a 1-pole lowpass filter (cutoff 800 Hz) to all harmonics above fundamental.
    Apply subtle saturation (tanh) to add warmth without harshness.
    Output is mono (mixed to L+R after binaural panning).
    """
```

### 1.4 Ambient Pad Generator (dsp/harmonic.py)

Four detuned oscillators (±3 cents, ±7 cents) per note, slowly evolving pitch via LFO (0.05 Hz):

```
Base note: carrier_freq × 0.5 (one octave below carrier)
Four voices: carrier×0.5 × [0.9983, 0.9996, 1.0004, 1.0017]
LFO modulates detune: ±1.5 cents at 0.05 Hz (20-second cycle)
Amplitude envelope: slow attack 4s, sustained, slow release 4s on stop
```

Apply reverb via a simple Schroeder reverberator (4 comb + 2 allpass filters) with a 2-second tail. Keep the reverb tail mono and mix into both channels equally.

### 1.5 Noise Layer (dsp/harmonic.py)

Pink noise generator (sum of 5 first-order filters as per Voss algorithm). Apply bandpass filter:
- For sleep presets: 200–800 Hz, very low amplitude (0.02)
- For focus presets: 400–4000 Hz ("brown noise" feel), amplitude 0.03
- For meditation: 100–1200 Hz, amplitude 0.015

### 1.6 Master Limiter (dsp/core.py)

Replace the current `apply_dB_limiter` with a true lookahead limiter:

```
Lookahead: 5ms (220 samples at 44100)
Attack: 1ms
Release: 100ms
Threshold: -3 dBFS
Output ceiling: -0.5 dBFS (prevent inter-sample peaks)
```

Use a circular buffer for lookahead. The gain computer uses a smoothed peak envelope detector.

### 1.7 Unit Tests (tests/test_dsp.py)

Write tests covering:
- `BinauralGenerator`: verify beat frequency accuracy (measure FFT peak of `right - left`)
- Phase continuity: generate 3 consecutive frames, concatenate, verify no phase jump
- Frequency glide: verify exponential convergence to target within 500ms
- Limiter: verify output never exceeds -0.5 dBFS given a full-scale sine
- Isochronic: verify amplitude envelope period matches beat frequency

---

## Phase 2 — Session Engine (Week 3–4)

### 2.1 Session Timeline (sessions/timeline.py)

New class `SessionTimeline` representing an automated session as a list of `TimelineSegment` objects:

```python
@dataclass
class TimelineSegment:
    name: str               # Display name for this segment
    start_time: float       # Seconds from session start
    beat_frequency: float   # Target beat Hz for this segment
    carrier_frequency: float
    ambient_layer: str      # "pad_soft", "pad_dark", "rain", "drone"
    noise_type: str         # "pink", "brown", "off"
    harmonic_richness: float  # 0.0..1.0 — how many overtones active
    transition_duration: float  # Seconds to glide from previous segment
    ease_type: str          # "linear", "ease_in", "ease_out", "ease_in_out", "exponential"
```

The `SessionController` reads a `SessionTimeline` and, as playback progresses, instructs `AudioMixer` to update parameters.

### 2.2 Sleep Descent Timeline

The sleep descent session is the most sophisticated and should be the flagship demo:

| Segment | Time | Beat | Carrier | Label | Ease |
|---------|------|------|---------|-------|------|
| Wake (beta) | 0:00 | 16 Hz | 240 Hz | Winding down | ease_out |
| Transition | 2:30 | 10 Hz | 220 Hz | Relaxing | ease_in_out |
| Alpha | 5:00 | 8 Hz | 200 Hz | Letting go | ease_in_out |
| Low Alpha | 8:00 | 7 Hz | 190 Hz | Drifting | ease_out |
| Theta entry | 12:00 | 5 Hz | 180 Hz | Dreaming | ease_in_out |
| Deep theta | 18:00 | 4 Hz | 165 Hz | Deep drift | exponential |
| Delta entry | 25:00 | 2.5 Hz | 150 Hz | Sleeping | exponential |
| Deep delta | 35:00 | 1.5 Hz | 140 Hz | Deep sleep | linear |

Transitions are 90 seconds each (the human brain needs ~60–90 seconds to respond to frequency shifts).

### 2.3 Focus Session (steady-state, no descent)

Focus sessions do NOT use descending timelines. They remain stable at the target frequency because we want beta-band alertness. Instead, they use a 4-minute rhythmic "reset cycle":

| Segment | Duration | What changes |
|---------|----------|--------------|
| Work | 3:00 | Steady at target |
| Micro-reset | 0:30 | Drop 2 Hz for 30s |
| Resume | 0:30 | Return to target |

Repeat the reset cycle every 4 minutes. This prevents entrainment fatigue.

### 2.4 Preset Definitions (sessions/controller.py)

Add metadata to the `Preset` dataclass for UI display:

```python
@dataclass
class Preset:
    name: str
    category: PresetCategory
    beat_frequency: float
    carrier_frequency: float = 220.0
    duration: float = 60.0
    drift_rate: float = 0.0
    # NEW UI metadata:
    description: str = ""        # One-line description for preset card
    brainwave_band: str = ""     # "Delta", "Theta", "Alpha", "Beta", "Gamma"
    color_theme: str = "cyan"    # Maps to UI theme: "cyan", "violet", "amber", "rose"
    recommended_duration: float = 1800.0  # Seconds (shown to user as "30 min")
    headphones_required: bool = True      # False for isochronic-only presets
```

### 2.5 Tests (tests/test_sessions.py)

- Verify `SessionTimeline` progresses correctly through segments
- Verify transition frequency at t=30s into a 90s transition matches easing formula
- Verify reset cycle triggers every 4 minutes on focus presets

---

## Phase 3 — Web UI (web.py) — Full Rebuild (Week 5–6)

The web interface in `neurosync/app/web.py` is the primary deliverable for the MVP (before PySide6/QML is complete). It must be production-quality.

### 3.1 Visual Design Direction

**Aesthetic:** Neuro-cyberpunk glassmorphism. Think medical imaging meets underground Berlin techno club. Not garish — precise. The palette should feel like a brain scanner's interface.

**Typography:**
- Display headings: `'Rajdhani'` (Google Fonts) — condensed, technical, futuristic
- UI labels and body: `'JetBrains Mono'` (Google Fonts) — monospaced, clinical, readable
- Frequency numbers: `'Orbitron'` — iconic sci-fi digits

**Color palette (CSS variables in `:root`):**
```css
--c-bg:           #050508;      /* Near-black with slight blue tint */
--c-surface:      #0c0c14;      /* Cards and panels */
--c-surface-2:    #13131f;      /* Slightly lighter surface */
--c-border:       rgba(0,255,200,0.12);  /* Teal glass border */
--c-border-glow:  rgba(0,255,200,0.35);  /* Hover/active glow */
--c-cyan:         #00ffc8;      /* Primary accent */
--c-cyan-dim:     rgba(0,255,200,0.15);  /* Cyan fill */
--c-violet:       #8b5cf6;      /* Secondary accent */
--c-violet-dim:   rgba(139,92,246,0.15); /* Violet fill */
--c-rose:         #f43f5e;      /* Alert / right hemisphere */
--c-rose-dim:     rgba(244,63,94,0.15);  /* Rose fill */
--c-amber:        #f59e0b;      /* Warning / active state */
--c-text:         #e2e8f0;      /* Primary text */
--c-text-dim:     #64748b;      /* Secondary text */
--c-text-hint:    #334155;      /* Disabled / ghost text */
```

**Glassmorphism cards:**
```css
.glass-card {
    background: rgba(13,13,20,0.8);
    backdrop-filter: blur(12px) saturate(1.4);
    -webkit-backdrop-filter: blur(12px) saturate(1.4);
    border: 1px solid var(--c-border);
    border-radius: 16px;
}
.glass-card:hover {
    border-color: var(--c-border-glow);
    box-shadow: 0 0 24px rgba(0,255,200,0.08), 0 0 1px var(--c-cyan);
}
```

### 3.2 Page Layout (HTML structure)

```
<body>
  <div id="bg-canvas"></div>          <!-- Animated particle/wave background (canvas) -->
  <header>                            <!-- Logo + version + connection status -->
  <main>
    <section id="brain-display">      <!-- Central brain visualization (SVG) -->
    <section id="freq-display">       <!-- L/R/Beat frequency numerals -->
    <section id="waveform-display">   <!-- Dual waveform canvas (L=cyan, R=violet) -->
    <section id="session-controls">   <!-- Play/Stop, volume, mode toggle -->
    <section id="preset-grid">        <!-- Animated preset cards grid -->
    <section id="parameter-panel">    <!-- Beat Hz, carrier Hz, layer controls -->
    <section id="session-timeline">   <!-- Visual timeline progress bar (for descent sessions) -->
  </main>
  <footer>                            <!-- Binaural warning, version -->
```

### 3.3 Brain Visualization (SVG, inline in HTML)

This is the centrepiece of the UI. It must be engineered, not decorative.

**Structure:** An SVG rendering of a simplified human brain viewed from above (coronal/axial view), with clearly separated left and right hemispheres.

**Implementation details:**

```
Outer skull outline: ellipse, rx=220 ry=180, centered at (400, 200)
  - Fill: #0a0a12
  - Stroke: 1px, var(--c-border)

Left hemisphere (L): half-ellipse on the left, fill animated with cyan pulse
Right hemisphere (R): half-ellipse on the right, fill animated with violet pulse

Corpus callosum divider: vertical line with slight wave, 2px, rgba(255,255,255,0.15)

Left hemisphere cortex folds (gyri/sulci): 6-8 curved SVG paths
  - Not anatomically precise — simplified, symmetric appearance
  - Stroke only (no fill), 0.8px, rgba(0,255,200,0.15)
  - Animate stroke-dashoffset on active state for "neural firing" effect

Right hemisphere cortex folds: mirrored counterpart
  - Stroke only, 0.8px, rgba(139,92,246,0.15)

Left frequency label: text element "L" + "220 Hz" centered in left hemisphere
Right frequency label: text element "R" + "230 Hz" centered in right hemisphere

Binaural beat label: centered below the brain, "BEAT: 10 Hz", "THETA"

Outer ring: circle (slightly larger than skull), stroke-dasharray animated
  - Pulses at beat frequency: CSS animation duration = 1/beat_freq seconds
  - Color: var(--c-cyan), opacity 0.4
```

**Hemisphere pulse animation:**
```css
@keyframes hemisphere-pulse-left {
    0%, 100% { fill: rgba(0, 255, 200, 0.04); }
    50%       { fill: rgba(0, 255, 200, 0.18); }
}
@keyframes hemisphere-pulse-right {
    0%, 100% { fill: rgba(139, 92, 246, 0.04); }
    50%       { fill: rgba(139, 92, 246, 0.18); }
}
```

The right hemisphere pulse is offset by exactly half the beat period (180°), simulating the binaural alternation between ears. Implement this by setting `animation-delay: calc(-1 * var(--beat-half-period))` on the right hemisphere, where `--beat-half-period` is set via JavaScript when the beat frequency changes.

**Neural activity dots:**
Scatter 12 small circles (r=2.5) across each hemisphere at fixed positions. On playback, animate them with staggered `opacity` pulses at the beat frequency, creating a "neural firing" impression.

**Brainwave band indicator:**
A label below the SVG that auto-updates: "DELTA 0.5–4 Hz", "THETA 4–8 Hz", etc., with a colored dot matching the band's color:
- Delta: indigo/navy (#4338ca)
- Theta: violet (#8b5cf6)
- Alpha: cyan (#06b6d4)
- Beta: emerald (#10b981)
- Gamma: rose (#f43f5e)

### 3.4 Waveform Display (Canvas API)

A dual-channel waveform viewer showing the binaural beat wave in real time.

**Canvas dimensions:** 100% width × 140px height
**Canvas ID:** `#waveform-canvas`

**Rendering (JavaScript, requestAnimationFrame loop):**
```
Left channel waveform: drawn from left=0 to right=canvas.width
  - Color: var(--c-cyan) (#00ffc8), lineWidth: 1.5
  - Y range: [20px, 70px] (upper half of canvas)
  - Render 2 full cycles of the carrier wave

Right channel waveform: drawn in lower half [75px, 125px]
  - Color: var(--c-violet) (#8b5cf6), lineWidth: 1.5
  - Y offset by (beat_phase / (2π)) × canvas_width — this shows the phase drift

Phase difference visualization:
  - A vertical "ghost" line sweeps left-to-right at beat_frequency Hz
  - Color: rgba(255,255,255,0.08)
  - Indicates the current beat cycle position

Background grid:
  - Horizontal center line at y=40px (upper half) and y=100px (lower half)
  - Color: rgba(255,255,255,0.04), 0.5px
```

**Beat cycle indicator:**
Below the waveform, a horizontal progress bar fills and resets at `beat_frequency` Hz, showing position within the current beat cycle. Color transitions from cyan (0%) to violet (50%) to cyan (100%).

### 3.5 Frequency Display Panel

Styled like a medical instrument readout. Three columns:

```
LEFT EAR          BEAT             RIGHT EAR
[ 220.0 Hz ]   [ 10.0 Hz ]    [ 230.0 Hz ]
 CARRIER                         CARRIER+BEAT
```

Typography: `'Orbitron'` font, 32px for the frequency number, 10px for the label.
Colors: left=cyan, beat=white, right=violet.

Add a 7-segment LED digit style for the Hz numbers (pure CSS, using `font-feature-settings` or a CSS custom font). Alternatively, use an SVG 7-segment renderer.

The numbers update smoothly (CSS `transition: all 0.3s ease` on the content is insufficient — numbers must morph with a flip/scroll animation). Use CSS counter animation or a digit-by-digit DOM swap with CSS translate transitions.

### 3.6 Preset Cards Grid

**Grid layout:** `grid-template-columns: repeat(auto-fill, minmax(180px, 1fr))`, gap 12px.

**Card anatomy:**
```
┌─────────────────────────────┐
│  [Category icon]  [Band dot]│
│                             │
│  PRESET NAME                │  ← Rajdhani, 20px, white
│  Short description          │  ← JetBrains Mono, 11px, dim
│                             │
│  ● 10 Hz                    │  ← beat frequency
│  ─────────────────────────  │  ← thin divider
│  ◷ 30 min   🎧 Required     │  ← metadata row
└─────────────────────────────┘
```

**Card states:**
- Default: glass card, dark
- Hover: border glows with category color (cyan/violet/amber/rose), slight scale(1.02) transform
- Active: solid border + colored background tint + "ACTIVE" badge top-right
- Loading: shimmer animation (skeleton loader) on first load

**Card click behavior:**
1. Apply `.active` class immediately (visual feedback < 16ms)
2. Call `loadPreset(name)` which updates oscillator frequencies via WebAudio API
3. Update brain visualization colors and pulse speed
4. Update waveform display and frequency readout
5. If a session timeline exists, display the timeline segment indicator

**Hover animation — category color sweep:**
```css
.preset-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 16px;
    background: linear-gradient(135deg, var(--card-color-dim) 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.preset-card:hover::before { opacity: 1; }
```

### 3.7 Parameter Control Panel

**Layout:** horizontal strip below preset cards.

**Beat frequency slider:**
- Range: 0.5 Hz – 40 Hz
- Step: 0.1 Hz
- Display: large number + brainwave band label
- Input type: custom range slider (no native browser styling)
- On change: smooth glide to new frequency (don't snap — use WebAudio `setTargetAtTime` with timeConstant 0.1)

**Carrier frequency slider:**
- Range: 100 Hz – 400 Hz
- Step: 1 Hz
- Display: number + note name (A3=220, etc.)
- Recommended carrier frequencies displayed as tick marks: 136.1 Hz (Earth frequency), 173.6 Hz, 221.2 Hz (Schumann resonance harmonic), 256 Hz, 432 Hz (concert A)

**Volume control:**
- Logarithmic scaling (not linear). Volume 50% on the slider should produce ~50% perceived loudness.
- Implementation: `gain = Math.pow(sliderValue/100, 2)` — this approximates equal-loudness contours.

**Layer toggles (checkboxes styled as pill toggles):**
- [ ] Harmonic Stack — adds overtones for warmth
- [ ] Isochronic Layer — speaker-compatible pulsing (works without headphones)
- [ ] Ambient Pads — generative pad background
- [ ] Pink Noise — gentle background noise floor

**Headphones warning:**
If isochronic layer is OFF and only binaural beats are active, display: `🎧 Headphones required for binaural effect` in amber, below the toggles.

### 3.8 Session Timeline Visualizer

For sessions with a `SessionTimeline` (e.g., Sleep Descent), display a horizontal progress indicator:

```
Beta 16Hz ──●──── Alpha 8Hz ────── Theta 4Hz ──── Delta 2Hz
  [0:00]   [5:00]               [12:00]          [25:00]    [60:00]
                  ↑ YOU ARE HERE (0:04:22)
```

- The timeline track is a horizontal bar, full width of the container
- Segments are proportionally sized by duration
- Each segment is color-coded by brainwave band
- The "you are here" indicator is a vertical line with elapsed time label
- Segment transitions are shown as gradient blends between band colors

### 3.9 Background Canvas Animation

The page background has a subtle animated canvas:

**Type:** Perlin noise field with flowing particles.

**Parameters:**
- 80–120 particles on desktop, 40 on mobile
- Particle movement follows a noise vector field (use a simple sine-based approximation if Perlin is too heavy)
- Particle color: cycle through `var(--c-cyan)` → `var(--c-violet)` based on x position
- Particle opacity: 0.15–0.35
- Particle size: 1–2px dots
- Speed scales with beat frequency (faster at beta, slower at delta)

**Performance:** Use `requestAnimationFrame`, respect `prefers-reduced-motion: reduce` (disable animation entirely if user prefers).

### 3.10 Mobile Responsiveness

Below 768px:
- Brain SVG scales to 100% width (viewBox preserves aspect ratio)
- Preset grid: 2 columns
- Waveform canvas: 80px height
- Parameter panel: vertical stack instead of horizontal
- Session timeline: hidden (too complex for mobile)

Below 480px:
- Preset grid: 1 column
- Brain SVG: 80% width, centered
- Frequency display: stacked vertically

### 3.11 Web.py FastAPI Endpoints (new)

```python
GET  /                          → Main HTML interface
GET  /api/status                → {version, is_playing, current_preset, session_elapsed}
POST /api/session/{preset_name} → Start session with preset
POST /api/session/stop          → Stop playback
GET  /api/presets               → Return all preset definitions as JSON
GET  /api/frequency             → Current {carrier, beat, left, right, band}
POST /api/frequency             → Set frequency {carrier?, beat?}
GET  /api/timeline/{preset}     → Return timeline segments for preset
WS   /ws/audio-state            → WebSocket: push frequency/amplitude state at 10 Hz for visualization
```

The WebSocket endpoint pushes real-time state (JSON) to connected clients, enabling smooth animation without polling.

---

## Phase 4 — PySide6 / QML UI (Week 7–8)

The QML UI mirrors the web UI aesthetics but is native desktop, with MIDI support and advanced visualizers.

### 4.1 UIBridge (ui/bridge.py)

```python
class UIBridge(QObject):
    """Exposes DSP state to QML via Qt Property/Signal system."""

    # Signals (Python → QML)
    carrierFreqChanged = Signal(float)
    beatFreqChanged    = Signal(float)
    amplitudeChanged   = Signal(float)
    bandChanged        = Signal(str)
    presetChanged      = Signal(str)
    sessionProgress    = Signal(float)   # 0.0..1.0

    @Property(float, notify=carrierFreqChanged)
    def carrierFreq(self): return self._carrier_freq

    @Slot(str)
    def loadPreset(self, name: str): ...

    @Slot(float)
    def setBeatFrequency(self, hz: float): ...

    @Slot()
    def startPlayback(self): ...

    @Slot()
    def stopPlayback(self): ...
```

### 4.2 QML Structure (neurosync/ui/qml/)

```
main.qml                  ← ApplicationWindow, loads MainView
views/
    MainView.qml          ← Root layout, references all panels
    PresetView.qml        ← Preset card grid (GridView)
    SessionView.qml       ← Active session timeline view
components/
    BrainVisualizer.qml   ← Animated SVG brain (ShaderEffect or Canvas)
    FrequencyKnob.qml     ← Custom rotary knob control
    WaveformDisplay.qml   ← Canvas-based dual waveform
    PresetCard.qml        ← Single preset card with hover animation
    BeatIndicator.qml     ← Pulsing beat frequency ring
    FrequencyReadout.qml  ← Orbitron-styled digit display
    LayerToggle.qml       ← Pill toggle for audio layers
    SessionTimeline.qml   ← Horizontal timeline progress
themes/
    DarkTheme.qml         ← Color palette and typography
    Typography.qml        ← Font sizes and weights
```

### 4.3 FrequencyKnob.qml — Implementation Spec

The primary rotary knob (beat frequency control) is a custom Canvas item:

```
Outer ring: dashed circle, 200px diameter, 24 tick marks
  - Ticks represent specific frequencies (labeled at Delta/Theta/Alpha/Beta boundaries)
  - Active range highlight: arc from min to current position, cyan fill

Inner disc: filled circle, 160px, deep black + subtle radial gradient

Needle: thin line from center to rim, rotates with value
  - Color: cyan glow (CSS: filter: drop-shadow(0 0 4px var(--c-cyan)))

Center label:
  - Top: current beat Hz (Orbitron, 28px)
  - Bottom: band name (Rajdhani, 14px, color = band color)

Interaction:
  - Mouse drag: vertical drag maps to ±5 Hz per 100px
  - Mouse wheel: 0.1 Hz per tick
  - Double-click: enter numeric input mode (shows text field)
  - Touch: pinch = coarse, single drag = fine

Animation: On preset load, the needle sweeps to the new position over 0.8s
  with an overshoot (spring animation: cubic bezier(0.34, 1.56, 0.64, 1))
```

### 4.4 BrainVisualizer.qml — Implementation Spec

Use QML `Canvas` element (not SVG, for performance):

```qml
Canvas {
    id: brainCanvas
    width: 400; height: 340
    
    // Redraw at 30fps via Timer
    // Draw order:
    // 1. Outer orbit ring (animated stroke-dashoffset)
    // 2. Skull ellipse (static)
    // 3. Left hemisphere (animated fill opacity)
    // 4. Right hemisphere (animated fill opacity, offset by half beat period)
    // 5. Cortex fold lines (6 each side, thin, pulsing opacity)
    // 6. Neural activity dots (12 each side, staggered opacity)
    // 7. Corpus callosum divider
    // 8. Frequency labels (center-positioned text)
    // 9. Beat frequency ring (outermost, pulses at beat_freq)
}
```

Use `property real beatProgress: 0.0` updated by a `NumberAnimation` with `duration: 1000 / bridge.beatFreq` in a loop. Both hemispheres reference this to calculate their pulse offset.

### 4.5 MIDI Support (audio/midi.py)

```python
import rtmidi  # requires python-rtmidi

class MidiController:
    """Maps MIDI CC to DSP parameters."""
    
    CC_BEAT_FREQ     = 1   # Mod wheel
    CC_CARRIER_FREQ  = 7   # Volume fader
    CC_LAYER_BINAURAL = 20
    CC_LAYER_ISO      = 21
    CC_LAYER_AMBIENT  = 22
    
    def on_message(self, message, data):
        status, cc, value = message[0]
        if status == 0xB0:  # Control Change
            normalized = value / 127.0
            if cc == self.CC_BEAT_FREQ:
                # Map 0..1 to 0.5..40 Hz (logarithmic)
                hz = 0.5 * (40/0.5) ** normalized
                self.dsp_bridge.set_target_beat(hz)
```

---

## Phase 5 — Visual System (Week 9)

### 5.1 FFT Visualizer (visualizers/engine.py)

Replace the current FFT implementation with a proper windowed FFT:

```python
def compute_fft_bands(self, left: np.ndarray, right: np.ndarray, n_bands: int = 32) -> np.ndarray:
    """
    Compute mel-scaled FFT bands from stereo audio.
    
    Uses Hann window to reduce spectral leakage.
    Averages L+R for mono FFT.
    Maps FFT bins to mel-scale bands (perceptually uniform).
    Applies temporal smoothing: bands[i] = 0.7 × bands[i] + 0.3 × new_bands[i]
    
    Returns:
        Array of n_bands values, normalized 0..1
    """
    mono = (left + right) * 0.5
    window = np.hanning(len(mono))
    spectrum = np.abs(np.fft.rfft(mono * window))
    # Map to mel bands... (see scipy.signal.mel_filter_bank)
```

### 5.2 Particle Background (visualizers/particles.py)

Upgrade `AmbientParticles` (with the BUG-001 fix applied):

- Separate `slow_particles` (30, large, 3–5px, slow, high opacity)  and `fast_particles` (200, tiny, 1px, faster, low opacity)
- Particle color and speed react to current brainwave band:
  - Delta: only slow particles, dark blue/indigo tones
  - Theta: slow + few fast, violet tones
  - Alpha: balanced, cyan tones
  - Beta: mostly fast, bright cyan/white
  - Gamma: all fast, white flashes
- Particles wrap at screen edges (torus topology)

### 5.3 Frequency Rings (visualizers/engine.py)

The `FrequencyRings` visualizer should render as a QML Canvas item. Use the FFT bands output as radius modulation:

```
5 rings, base radius 80px → 120px → 160px → 200px → 240px
Each ring's radius modulated by ±20px based on its assigned FFT band
Ring opacity: 0.6 for inner, decreasing to 0.2 for outermost
Ring stroke width: 2px inner, 0.5px outermost
Ring color: gradient from cyan (inner) → violet (outer)
Animation: rotate slowly (0.02 rad/s for inner, opposite direction for outer)
```

---

## Phase 6 — Ambient Music Engine (Week 10)

### 6.1 House Music Integration

The "house music feel" from the concept is achieved via a rhythmic sub-bass pulse, not a full drum kit:

**Sub-bass pulse generator (dsp/harmonic.py):**
```
For FOCUS and CREATIVITY presets only.
A 40–60 Hz sine wave (sub-bass) amplitude-modulated by a 4/4 kick pattern:
  Beat pattern: 1.0, 0.0, 0.7, 0.0, 1.0, 0.0, 0.7, 0.0 (8 steps per bar)
  BPM: 60–70 BPM (relaxed pace, not energetic)
  Each amplitude value is a smooth ramp (cosine), not a hard gate
  Volume: very low (0.08 max gain) — felt not heard

Sidechain effect on ambient pads:
  When sub-bass pulse fires, reduce pad gain to 0.7 for 80ms, then return to 1.0
  This gives the characteristic pumping feel without any compression plugin
```

### 6.2 Session Presets — Complete Ambient Profiles

Each preset category has an ambient audio signature:

| Category | Pad | Sub | Noise | Reverb |
|----------|-----|-----|-------|--------|
| Sleep | Sine choir, slow vibrato | None | Pink 0.02 | Very long (4s) |
| Focus | Clean detuned saw pad | Subtle pulse 65 BPM | Brown 0.03 | Short (0.8s) |
| Meditation | Bell-like FM pad | None | Pink 0.015 | Long (3s) |
| Creativity | Warm analog pad | Light pulse 60 BPM | Pink 0.02 | Medium (1.5s) |

---

## Phase 7 — Packaging & Testing (Week 11–12)

### 7.1 Full Test Suite (tests/)

```
tests/
├── test_dsp.py           ← Phase 1 tests (BinauralGenerator, limiter, isochronic)
├── test_sessions.py      ← Phase 2 tests (timeline, transitions)
├── test_mixer.py         ← Phase 6 tests (layer mixing, headroom)
├── test_web_api.py       ← FastAPI endpoint tests (httpx + pytest-asyncio)
├── test_visualizers.py   ← FFT bands, particle physics
└── conftest.py           ← Shared fixtures (sample_rate, sample audio data)
```

All tests must pass in under 30 seconds total (no real-time audio output in tests — mock sounddevice).

**Mock sounddevice pattern:**
```python
# conftest.py
@pytest.fixture(autouse=True)
def mock_sounddevice(monkeypatch):
    """Prevent tests from touching audio hardware."""
    import sounddevice as sd
    monkeypatch.setattr(sd, 'OutputStream', MockOutputStream)
```

### 7.2 Performance Targets

Measure and enforce these benchmarks (add to CI):
- DSP callback latency: < 2ms for 1024-sample frame at 44100 Hz
- CPU usage: < 5% single core during steady-state playback
- UI frame rate: ≥ 30 FPS during active visualization
- Memory: < 200 MB total process (DSP + UI + visualizer)

### 7.3 Docker (updated Dockerfile)

Per RULES_coding.md: base image must be `debian:12-slim`.

```dockerfile
FROM debian:12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3-pip \
    portaudio19-dev \
    libsndfile1 \
    libfftw3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY . .

EXPOSE 8045

CMD ["python3", "-m", "neurosync.app.web"]
```

Note: PySide6/QML does not run inside Docker (no display server). The Docker image runs the web interface only. Desktop QML app is distributed via PyInstaller.

### 7.4 PyInstaller Configuration (neurosync.spec)

```python
# neurosync.spec
a = Analysis(
    ['neurosync/app/main.py'],
    datas=[
        ('neurosync/ui/qml', 'neurosync/ui/qml'),
        ('neurosync/presets', 'neurosync/presets'),
        ('neurosync/config', 'neurosync/config'),
    ],
    hiddenimports=['sounddevice', 'numpy', 'scipy'],
)
```

### 7.5 CI/CD (.github/workflows/ci.yml)

```yaml
name: NeuroSync CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install PortAudio
        run: sudo apt-get install -y portaudio19-dev libsndfile1
      - name: Setup Python
        uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - name: Install deps
        run: pip install -e ".[dev]"
      - name: Lint (ruff)
        run: ruff check neurosync/
      - name: Type check (mypy)
        run: mypy neurosync/ --ignore-missing-imports
      - name: Run tests
        run: pytest tests/ --cov=neurosync --cov-report=xml
      - name: Coverage gate
        run: coverage report --fail-under=80
```

---

## Phase 8 — Neuroscience Enhancements (Ongoing)

### 8.1 Schumann Resonance Carrier Mode

The Earth's electromagnetic resonance at 7.83 Hz (and harmonics: 14.3, 20.8, 27.3 Hz) have been studied in relation to brain synchronization. Add carrier frequency presets at Schumann-resonance harmonics:
- 136.1 Hz (Earth year frequency)
- 172.0 Hz (Earth day frequency)
- 221.2 Hz (popular "healing frequency")

These are selectable in the carrier frequency picker as named tick marks.

### 8.2 Frequency Accuracy Specification

The binaural beat frequency accuracy must be within 0.01 Hz at 44100 Hz sample rate. Verify:
- At 10 Hz beat with 44100 Hz sample rate, right_freq - left_freq = 10.0 Hz exactly
- The BinauralGenerator phase accumulation must use `float64` (not float32) to prevent accumulated phase drift over long sessions

### 8.3 Safety Limits

Hard-code the following in AudioMixer, not adjustable by user:
- Minimum beat frequency: 0.5 Hz (below this, isochronic pulses are too slow to be safe)
- Maximum beat frequency: 40 Hz (above gamma band, no known benefit)
- Maximum carrier frequency: 500 Hz (above this, binaural effect is less reliable)
- Maximum output level: -3 dBFS (limiter enforced, not a soft limit)
- Startup volume ramp: 3-second linear fade-in on first start

Add an audio safety disclaimer in the UI footer: "Use at safe listening volumes. Not recommended for people with epilepsy or seizure disorders. Not a medical device."

---

## Updated Milestone Deliverables

| Milestone | Target | Description | Definition of Done |
|-----------|--------|-------------|-------------------|
| M0: Bug fixes | Week 1 Day 1–2 | Fix BUG-001..006 | All existing tests pass, no phase clicks in audio |
| M1: DSP Core v2 | Week 2 | Stateful binaural + isochronic + harmonic | Unit tests pass, <0.01 Hz accuracy verified |
| M2: Web UI v2 | Week 6 | Full web interface with brain visualization | Brain SVG animates, presets work, stereo routing confirmed |
| M3: Session Engine | Week 4 | Full timeline for Sleep Descent | Timeline segments tested, smooth transitions verified |
| M4: QML UI Alpha | Week 8 | Native desktop with FrequencyKnob | FrequencyKnob interactive, UIBridge signals firing |
| M5: Ambient Engine | Week 10 | Full ambient layer + house integration | All layers mix correctly, no clipping at full amplitude |
| M6: Production | Week 12 | Docker, PyInstaller, CI/CD | Docker builds cleanly, tests > 80% coverage, CI green |

---

## File Change Summary

| File | Action | Reason |
|------|--------|--------|
| `neurosync/dsp/core.py` | Modify | Add `BinauralGenerator`, fix drift bug, improve limiter |
| `neurosync/dsp/harmonic.py` | Create | Harmonic stack, ambient pads, noise, reverb |
| `neurosync/dsp/isochronic.py` | Create | Isochronic tone generator |
| `neurosync/audio/engine.py` | Modify | Use `BinauralGenerator`, add phase continuity |
| `neurosync/audio/mixer.py` | Create | Multi-layer audio mixer |
| `neurosync/audio/midi.py` | Create | MIDI CC controller mapping |
| `neurosync/sessions/controller.py` | Modify | Add metadata to `Preset`, remove duplicate PRESETS dict |
| `neurosync/sessions/timeline.py` | Create | `SessionTimeline`, `TimelineSegment` |
| `neurosync/presets/defs.py` | Modify | Remove duplicate PRESETS dict, import from controller |
| `neurosync/visualizers/engine.py` | Modify | Fix particle bug, windowed FFT, mel bands |
| `neurosync/visualizers/particles.py` | Create | Upgraded particle system |
| `neurosync/ui/bridge.py` | Create | QObject UIBridge for QML |
| `neurosync/ui/qml/main.qml` | Rewrite | Full QML UI structure |
| `neurosync/ui/qml/components/BrainVisualizer.qml` | Create | Canvas brain animation |
| `neurosync/ui/qml/components/FrequencyKnob.qml` | Create | Rotary knob control |
| `neurosync/ui/qml/components/WaveformDisplay.qml` | Create | Dual waveform canvas |
| `neurosync/ui/qml/components/PresetCard.qml` | Create | Animated preset card |
| `neurosync/ui/qml/components/SessionTimeline.qml` | Create | Timeline progress |
| `neurosync/app/web.py` | Rewrite | Full web UI with brain SVG, stereo fix, WebSocket |
| `neurosync/app/main.py` | Modify | Inject UIBridge into QML engine |
| `tests/test_dsp.py` | Create | DSP unit tests |
| `tests/test_sessions.py` | Create | Session timeline tests |
| `tests/test_web_api.py` | Create | FastAPI endpoint tests |
| `tests/conftest.py` | Create | Shared test fixtures |
| `Dockerfile` | Modify | Switch to debian:12-slim |
| `docker-compose.yml` | Modify | Add ports.env reference |
| `ARCHITECTURE.md` | Update | New modules, data flow |
| `README.md` | Update | New features, WebSocket docs |

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

*Plan version 2.0 | NeuroSync v0.2.0 | 2026-05-24*
*Author: Inventions4All - github:TWeb79*