import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.main import app

client = TestClient(app)

def test_explore_status():
    response = client.get("/api/explore/status")
    assert response.status_code == 200
    data = response.json()
    assert "has_credentials" in data
    assert "message" in data

def test_explore_missions():
    response = client.get("/api/explore/missions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 12
    assert data[0]["title"].startswith("🏛️")

def test_explore_emergency():
    response = client.get("/api/explore/emergency?lat=28.6139&lng=77.2090")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    assert data[0]["category"] == "Hospital"

def test_explore_plan():
    payload = {
        "location": "Red Fort, Delhi",
        "available_hours": 6.0,
        "budget": 2000.0,
        "interests": ["Historical", "Food", "Photography"]
    }
    response = client.post("/api/explore/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "waiting_for_api_credentials" in data
    assert "location" in data

def test_explore_audio_guide():
    response = client.get("/api/explore/audio-guide/attr_red_fort?name=Red%20Fort")
    assert response.status_code == 200
    data = response.json()
    assert data["attraction_id"] == "attr_red_fort"
    assert "script" in data
