"""
Web Server for NeuroSync
Author: Inventions4All - github:TWeb79
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="NeuroSync v0.1.0")


@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serve the main web interface with audio binaural beat generator."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NeuroSync - Adaptive Brainwave Audio Studio</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #0a0a0a; color: #ffffff; min-height: 100vh; overflow-x: hidden; }
            .container { max-width: 900px; margin: 0 auto; padding: 30px; }
            h1 { color: #00ffff; text-align: center; font-size: 3em; margin-bottom: 10px; text-shadow: 0 0 20px #00ffff; }
            .subtitle { text-align: center; color: #888; margin-bottom: 40px; }
            
            .visualizer { text-align: center; margin: 40px 0; position: relative; height: 200px; }
            .brainwave-sphere { width: 150px; height: 150px; margin: 0 auto; border-radius: 50%; background: radial-gradient(circle, #00ffff 0%, #0a0a2a 70%); border: 2px solid #00ffff; animation: pulse 2s infinite; position: relative; }
            @keyframes pulse { 0%, 100% { transform: scale(1); box-shadow: 0 0 30px #00ffff; } 50% { transform: scale(1.1); box-shadow: 0 0 50px #00ffff, 0 0 80px #0088ff; } }
            .frequency-display { margin-top: 20px; color: #00ff00; font-size: 1.2em; }
            
            .presets { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 30px 0; }
            .preset-card { background: #1a1a2a; border: 1px solid #00ffff; border-radius: 10px; padding: 20px; text-align: center; cursor: pointer; transition: all 0.3s; }
            .preset-card:hover { background: #00ffff; color: #0a0a0a; transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0, 255, 255, 0.3); }
            .preset-card.active { background: #00ff00; color: #0a0a0a; border-color: #00ff00; animation: glow 1s infinite; }
            @keyframes glow { 0%, 100% { box-shadow: 0 0 20px #00ff00; } 50% { box-shadow: 0 0 40px #00ff00, 0 0 60px #00ff00; } }
            .preset-name { font-weight: bold; margin-bottom: 5px; }
            .preset-freq { color: #888; font-size: 0.9em; }
            
            .controls { display: flex; justify-content: center; gap: 20px; margin: 30px 0; flex-wrap: wrap; }
            .control-group { background: #1a1a2a; padding: 15px; border-radius: 10px; border: 1px solid #333; }
            .control-group label { display: block; margin-bottom: 5px; color: #888; font-size: 0.9em; }
            input[type="range"] { width: 200px; }
            
            .status { text-align: center; padding: 15px; background: #1a1a2a; border-radius: 10px; border: 1px solid #00ffff; color: #00ff00; margin-top: 20px; }
            .playing { color: #ff0066; animation: blink 1s infinite; }
            @keyframes blink { 50% { opacity: 0.5; } }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>NeuroSync</h1>
            <p class="subtitle">Adaptive Brainwave Audio Studio v0.1.0 (2026-05-24)</p>
            
            <div class="visualizer">
                <div class="brainwave-sphere" id="sphere"></div>
                <div class="frequency-display">
                    Beat: <span id="beat-freq">0.0</span> Hz | Carrier: <span id="carrier-freq">220.0</span> Hz
                </div>
            </div>
            
            <h3>Brainwave Presets</h3>
            <div class="presets" id="presets">
                <div class="preset-card" onclick="loadPreset('deep_sleep', 2, 180)"><div class="preset-name">Deep Sleep</div><div class="preset-freq">2 Hz</div></div>
                <div class="preset-card" onclick="loadPreset('rem_sleep', 4, 160)"><div class="preset-name">REM Sleep</div><div class="preset-freq">4 Hz</div></div>
                <div class="preset-card" onclick="loadPreset('power_nap', 6, 200)"><div class="preset-name">Power Nap</div><div class="preset-freq">6 Hz</div></div>
                <div class="preset-card" onclick="loadPreset('focus', 14, 220)"><div class="preset-name">Focus</div><div class="preset-freq">14 Hz</div></div>
                <div class="preset-card" onclick="loadPreset('deep_work', 18, 240)"><div class="preset-name">Deep Work</div><div class="preset-freq">18 Hz</div></div>
                <div class="preset-card" onclick="loadPreset('meditate', 7, 200)"><div class="preset-name">Meditate</div><div class="preset-freq">7 Hz</div></div>
                <div class="preset-card" onclick="loadPreset('creative', 7, 180)"><div class="preset-name">Creative</div><div class="preset-freq">7 Hz</div></div>
                <div class="preset-card" onclick="loadPreset('zen', 7, 150)"><div class="preset-name">Zen</div><div class="preset-freq">7 Hz</div></div>
            </div>
            
            <div class="controls">
                <div class="control-group">
                    <label for="beat-slider">Beat Frequency: <span id="beat-value">10</span> Hz</label>
                    <input type="range" id="beat-slider" min="1" max="30" value="10" oninput="updateFreqs()">
                </div>
                <div class="control-group">
                    <label for="carrier-slider">Carrier: <span id="carrier-value">220</span> Hz</label>
                    <input type="range" id="carrier-slider" min="100" max="400" value="220" oninput="updateFreqs()">
                </div>
                <div class="control-group">
                    <label>Volume: <span id="volume-value">50</span>%</label>
                    <input type="range" id="volume-slider" min="0" max="100" value="50" oninput="updateVolume()">
                </div>
            </div>
            
            <div class="status" id="status">Stopped - Click a preset to begin</div>
            <button onclick="togglePlayback()" style="padding: 15px 40px; font-size: 1.2em; background: #00ffff; color: #0a0a0a; border: none; border-radius: 10px; cursor: pointer; margin: 20px auto; display: block;">Play / Stop</button>
        </div>
        
        <script>
            let audioCtx = null;
            let leftOsc = null, rightOsc = null;
            let leftGain = null, rightGain = null;
            let beatFreq = 10, carrierFreq = 220;
            let isPlaying = false;
            
            function initAudio() {
                if (!audioCtx) {
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    leftOsc = audioCtx.createOscillator();
                    rightOsc = audioCtx.createOscillator();
                    leftGain = audioCtx.createGain();
                    rightGain = audioCtx.createGain();
                    
                    leftOsc.type = 'sine';
                    rightOsc.type = 'sine';
                    
                    leftOsc.connect(leftGain);
                    rightOsc.connect(rightGain);
                    leftGain.connect(audioCtx.destination);
                    rightGain.connect(audioCtx.destination);
                    
                    leftOsc.start();
                    rightOsc.start();
                }
            }
            
            function updateFreqs() {
                beatFreq = parseInt(document.getElementById('beat-slider').value);
                carrierFreq = parseInt(document.getElementById('carrier-slider').value);
                document.getElementById('beat-value').textContent = beatFreq;
                document.getElementById('carrier-value').textContent = carrierFreq;
                document.getElementById('beat-freq').textContent = beatFreq;
                document.getElementById('carrier-freq').textContent = carrierFreq;
                
                if (leftOsc && rightOsc) {
                    const leftFreq = carrierFreq;
                    const rightFreq = carrierFreq + beatFreq;
                    leftOsc.frequency.setValueAtTime(leftFreq, audioCtx.currentTime);
                    rightOsc.frequency.setValueAtTime(rightFreq, audioCtx.currentTime);
                }
            }
            
            function updateVolume() {
                const vol = parseInt(document.getElementById('volume-slider').value) / 100;
                document.getElementById('volume-value').textContent = Math.round(vol * 100);
                if (leftGain && rightGain) {
                    leftGain.gain.setValueAtTime(vol * 0.2, audioCtx.currentTime);
                    rightGain.gain.setValueAtTime(vol * 0.2, audioCtx.currentTime);
                }
            }
            
            function loadPreset(name, beat, carrier) {
                document.querySelectorAll('.preset-card').forEach(c => c.classList.remove('active'));
                event.target.closest('.preset-card').classList.add('active');
                
                beatFreq = beat; carrierFreq = carrier;
                document.getElementById('beat-slider').value = beat;
                document.getElementById('carrier-slider').value = carrier;
                document.getElementById('beat-value').textContent = beat;
                document.getElementById('carrier-value').textContent = carrier;
                document.getElementById('beat-freq').textContent = beat;
                document.getElementById('carrier-freq').textContent = carrier;
                
                if (leftOsc && rightOsc) {
                    const leftF = carrierFreq;
                    const rightF = carrierFreq + beatFreq;
                    leftOsc.frequency.setValueAtTime(leftF, audioCtx.currentTime);
                    rightOsc.frequency.setValueAtTime(rightF, audioCtx.currentTime);
                }
                document.getElementById('status').textContent = name + ' active';
            }
            
            function togglePlayback() {
                if (!audioCtx) {
                    initAudio();
                    updateFreqs();
                    updateVolume();
                }
                
                if (isPlaying) {
                    leftGain.gain.setValueAtTime(0, audioCtx.currentTime);
                    rightGain.gain.setValueAtTime(0, audioCtx.currentTime);
                    document.getElementById('status').textContent = 'Stopped';
                    document.getElementById('status').className = 'status';
                } else {
                    updateVolume();
                    document.getElementById('status').textContent = 'Playing...';
                    document.getElementById('status').className = 'status playing';
                }
                isPlaying = !isPlaying;
            }
        </script>
    </body>
    </html>
    """


@app.post("/api/session/{preset_name}")
def set_session(preset_name: str):
    """Set the current session preset."""
    return {"preset": preset_name, "status": "active"}


@app.get("/api/status")
def get_status():
    """Get current session status."""
    return {"version": "0.1.0", "status": "running"}


def main():
    """Run the web server."""
    import uvicorn
    port = int(os.environ.get("PORT", 8045))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()