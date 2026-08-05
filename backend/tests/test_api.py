import sys
import os
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_search():
    payload = {
        "origin": "Kanpur",
        "destination": "Bangalore",
        "start_date": "2026-10-15",
        "budget": 5000.0,
        "preferences": {"optimize_by": "cheapest"}
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "total_price" in data[0]
    assert "legs" in data[0]

def test_chat():
    payload = {
        "message": "Find me the cheapest route from Kanpur to Bangalore with budget 5000"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["itineraries"]) > 0

def test_analytics():
    response = client.get("/api/user/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "money_saved" in data
    assert "hours_saved" in data

def test_notifications():
    response = client.get("/api/notifications")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_auth_register_and_login():
    import time
    test_email = f"test_user_{int(time.time())}@travel.com"
    # 1. Register
    reg_resp = client.post("/api/auth/register", json={
        "email": test_email,
        "password": "password123",
        "name": "Audit Test User"
    })
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == test_email

    # 2. Login
    login_resp = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "password123"
    })
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    assert login_data["user"]["name"] == "Audit Test User"

def test_hotels_api():
    response = client.get("/api/hotels?destination=Bangalore")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "name" in data[0]
    assert "price_per_night" in data[0]

def test_hyperlocal_psit_kanpur_search():
    payload = {
        "origin": "PSIT Kanpur",
        "destination": "Bangalore",
        "start_date": "2026-10-15",
        "budget": 6000.0,
        "preferences": {"optimize_by": "best_value"}
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    # Check that first leg starts from PSIT Kanpur
    assert "Psit Kanpur" in data[0]["legs"][0]["origin"] or "PSIT Kanpur" in data[0]["legs"][0]["origin"]

def test_global_usa_international_search():
    payload = {
        "origin": "Kanpur",
        "destination": "USA",
        "start_date": "2026-10-15",
        "budget": 75000.0,
        "preferences": {"optimize_by": "best_value"}
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    # Ensure Flight is present and no long-haul intercity trains exist for travel to USA
    transport_types = [leg["transport_type"] for leg in data[0]["legs"]]
    assert "Train" not in transport_types
    assert "Flight" in transport_types

if __name__ == "__main__":
    test_root()
    test_search()
    test_chat()
    test_analytics()
    test_notifications()
    test_auth_register_and_login()
    test_hotels_api()
    test_hyperlocal_psit_kanpur_search()
    test_global_usa_international_search()
    print("ALL BACKEND AUDIT TESTS PASSED SUCCESSFULLY!")
