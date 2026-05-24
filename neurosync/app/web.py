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
            
            .brain-visualizer { display: flex; justify-content: center; align-items: center; margin: 40px 0; gap: 20px; }
            .brain-side { text-align: center; flex: 1; }
            .brain-hemisphere { width: 120px; height: 160px; margin: 0 auto; background: linear-gradient(135deg, #2a2a4a 0%, #0a0a2a 100%); border-radius: 60px 60px 50px 50px; border: 2px solid #00ffff; position: relative; overflow: hidden; }
            .brain-hemisphere::before { content: ''; position: absolute; top: 20px; left: 50%; transform: translateX(-50%); width: 40px; height: 40px; background: #00ff00; border-radius: 50%; animation: pulse 1s infinite; }
            @keyframes pulse { 0%, 100% { opacity: 0.5; transform: translateX(-50%) scale(1); } 50% { opacity: 1; transform: translateX(-50%) scale(1.2); } }
            .ear-label { color: #ff0066; font-weight: bold; margin-top: 15px; font-size: 1.4em; }
            .ear-freq { color: #00ffff; font-size: 1.2em; margin-top: 5px; }
            
            .brain-middle { flex: 0 0 80px; text-align: center; }
            .hemisync-display { width: 80px; height: 80px; margin: 0 auto; background: radial-gradient(circle, #ff0066 0%, #0a0a2a 70%); border-radius: 50%; border: 3px solid #ff0066; display: flex; align-items: center; justify-content: center; font-size: 1.5em; font-weight: bold; color: #ff0066; animation: beat-pulse var(--beat-duration, 0.5s) infinite; }
            @keyframes beat-pulse { 0%, 100% { transform: scale(1); box-shadow: 0 0 20px #ff0066; } 50% { transform: scale(1.1); box-shadow: 0 0 40px #ff0066, 0 0 60px #ff0066; } }
            .hemisync-label { margin-top: 10px; color: #ff0066; font-weight: bold; }
            
            .presets { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 30px 0; }
            .preset-card { background: #1a1a2a; border: 1px solid #00ffff; border-radius: 10px; padding: 20px; text-align: center; cursor: pointer; transition: all 0.3s; }
            .preset-card:hover { background: #00ffff; color: #0a0a0a; transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0, 255, 255, 0.3); }
            .preset-card.active { background: #00ff00; color: #0a0a0a; border-color: #00ff00; }
            .preset-name { font-weight: bold; margin-bottom: 5px; }
            .preset-freq { color: #888; font-size: 0.9em; }
            
            .controls { display: flex; justify-content: center; gap: 20px; margin: 30px 0; flex-wrap: wrap; }
            .control-group { background: #1a1a2a; padding: 15px; border-radius: 10px; border: 1px solid #333; }
            .control-group label { display: block; margin-bottom: 5px; color: #888; font-size: 0.9em; }
            input[type="range"] { width: 200px; }
            
            .status { text-align: center; padding: 15px; background: #1a1a2a; border-radius: 10px; border: 1px solid #00ffff; color: #00ff00; margin-top: 20px; }
            .playing { color: #ff0066; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>NeuroSync</h1>
            <p class="subtitle">Adaptive Brainwave Audio Studio v0.1.0 (2026-05-24)</p>
            
            <div class="brain-visualizer">
                <div class="brain-side">
                    <div class="brain-hemisphere"></div>
                    <div class="ear-label">LEFT EAR</div>
                    <div class="ear-freq" id="left-freq">220.0 Hz</div>
                </div>
                
                <div class="brain-middle">
                    <div class="hemisync-display" id="beat-freq">10</div>
                    <div class="hemisync-label">HEMISYNC</div>
                </div>
                
                <div class="brain-side">
                    <div class="brain-hemisphere"></div>
                    <div class="ear-label">RIGHT EAR</div>
                    <div class="ear-freq" id="right-freq">230.0 Hz</div>
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
                    <label for="beat-slider">Beat: <span id="beat-value">10</span> Hz</label>
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
                document.getElementById('left-freq').textContent = carrierFreq + ' Hz';
                document.getElementById('right-freq').textContent = (carrierFreq + beatFreq) + ' Hz';
                
                document.getElementById('beat-freq').style.animationDuration = (1/beatFreq) + 's';
                
                if (leftOsc && rightOsc) {
                    leftOsc.frequency.setValueAtTime(carrierFreq, audioCtx.currentTime);
                    rightOsc.frequency.setValueAtTime(carrierFreq + beatFreq, audioCtx.currentTime);
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
                document.getElementById('left-freq').textContent = carrier + ' Hz';
                document.getElementById('right-freq').textContent = (carrier + beat) + ' Hz';
                document.getElementById('beat-freq').style.animationDuration = (1/beat) + 's';
                
                if (leftOsc && rightOsc) {
                    leftOsc.frequency.setValueAtTime(carrier, audioCtx.currentTime);
                    rightOsc.frequency.setValueAtTime(carrier + beat, audioCtx.currentTime);
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