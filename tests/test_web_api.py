"""
Tests for Web API
Author: Inventions4All - github:TWeb79
"""

import pytest
from fastapi.testclient import TestClient
from neurosync.app.web import app


@pytest.fixture
def client():
    return TestClient(app)


class TestWebAPI:
    """Tests for FastAPI web endpoints."""

    def test_get_status(self, client):
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "is_playing" in data

    def test_get_presets(self, client):
        response = client.get("/api/presets")
        assert response.status_code == 200
        data = response.json()
        assert "presets" in data
        assert len(data["presets"]) > 0

    def test_start_session(self, client):
        response = client.post("/api/session/coding_flow")
        assert response.status_code == 200
        data = response.json()
        assert data["preset"] == "coding_flow"

    def test_stop_session(self, client):
        response = client.post("/api/session/stop")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stopped"

    def test_get_frequency(self, client):
        response = client.get("/api/frequency")
        assert response.status_code == 200
        data = response.json()
        assert "carrier" in data
        assert "beat" in data
        assert "band" in data

    def test_get_timeline(self, client):
        response = client.get("/api/timeline/sleep_descent")
        assert response.status_code == 200
        data = response.json()
        assert "segments" in data

    def test_start_session_invalid(self, client):
        response = client.post("/api/session/unknown_preset")
        assert response.status_code == 404

    def test_set_frequency(self, client):
        response = client.post("/api/frequency")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"

    def test_get_timeline_unknown(self, client):
        response = client.get("/api/timeline/unknown")
        assert response.status_code == 200
        assert response.json()["segments"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])