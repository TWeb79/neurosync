"""
Web Server for NeuroSync
Author: Inventions4All - github:TWeb79
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="NeuroSync v0.2.0")

try:
    import socketio
    sio = socketio.AsyncServer(async_mode="asgi")
    socket_app = socketio.ASGIApp(sio)
    app.mount("/ws", socket_app)
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False


@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serve the main web interface."""
    return _get_html()


def _get_html() -> str:
    """Serve the neurosync_ui.html file."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    html_path = os.path.join(base_dir, "neurosync_ui.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<html><body><h1>NeuroSync UI not found</h1></body></html>"


@app.get("/api/status")
def get_status():
    """Get current session status."""
    return {"version": "0.2.0", "is_playing": False, "current_preset": None, "session_elapsed": 0}


@app.post("/api/session/stop")
def stop_session():
    """Stop the current session."""
    return {"status": "stopped", "message": "Session stopped"}


@app.post("/api/session/{preset_name}")
def start_session(preset_name: str):
    """Start a session with the given preset."""
    return {"preset": preset_name, "status": "active", "message": f"Session {preset_name} started"}


@app.get("/api/presets")
def get_presets():
    """Return all preset definitions."""
    return {
        "presets": [
            {"name": "deep_sleep", "beat": 2.0, "carrier": 180, "band": "delta", "duration": 3600, "description": "Deep delta waves", "color_theme": "indigo"},
            {"name": "sleep_descent", "beat": 16, "carrier": 240, "band": "beta", "duration": 3600, "description": "Full descent", "color_theme": "cyan"},
            {"name": "coding_flow", "beat": 14, "carrier": 220, "band": "beta", "duration": 2700, "description": "Focus session", "color_theme": "emerald"},
            {"name": "zen_meditation", "beat": 7, "carrier": 200, "band": "theta", "duration": 1800, "description": "Deep meditation", "color_theme": "violet"},
            {"name": "creative_flow", "beat": 8, "carrier": 180, "band": "theta", "duration": 1800, "description": "Creative state", "color_theme": "amber"},
            {"name": "adhd_focus", "beat": 12, "carrier": 200, "band": "alpha", "duration": 2400, "description": "ADHD focus", "color_theme": "cyan"},
        ]
    }


@app.get("/api/frequency")
def get_frequency():
    """Get current frequency state."""
    return {"carrier": 220.0, "beat": 10.0, "left": 220.0, "right": 230.0, "band": "alpha"}


@app.post("/api/frequency")
def set_frequency():
    """Set frequency values."""
    return {"status": "updated"}


@app.get("/api/timeline/{preset_name}")
def get_timeline(preset_name: str):
    """Return timeline segments for a preset."""
    timelines = {
        "sleep_descent": [
            {"name": "Beta", "beat": 16, "time": 0},
            {"name": "Alpha", "beat": 8, "time": 150},
            {"name": "Theta", "beat": 4, "time": 600},
            {"name": "Delta", "beat": 1.5, "time": 1500},
        ]
    }
    return {"segments": timelines.get(preset_name, [])}


def main():
    """Run the web server."""
    import uvicorn
    port = int(os.environ.get("PORT", 8045))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()