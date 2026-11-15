
import pytest
from copy import deepcopy
from app import app, bags


# ==========================================
# PYTEST FIXTURE: TEST CLIENT AND DATA RESET
# ==========================================

@pytest.fixture
def client():
    original_bags = deepcopy(bags)

    try:
        with app.test_client() as test_client:
            yield test_client
    finally:
        bags.clear()
        bags.update(original_bags)


# ==========================================
# TEST 1: HEALTH CHECK
# ==========================================

def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "healthy"


# ==========================================
# TEST 2: TRACK EXISTING BAG
# ==========================================

def test_track_existing_bag(client):
    response = client.get("/bags/BAG-10045")

    assert response.status_code == 200

    data = response.get_json()
    assert data["bag_tag"] == "BAG-10045"
    assert data["flight"] == "DL1254"
    assert data["current_status"] == "Loaded"


# ==========================================
# TEST 3: TRACK NONEXISTENT BAG
# ==========================================

def test_track_nonexistent_bag(client):
    response = client.get("/bags/BAG-99999")

    assert response.status_code == 404

    data = response.get_json()
    assert data["error"] == "Bag not found"


# ==========================================
# TEST 4: REGISTER NEW BAG
# ==========================================

def test_register_new_bag(client):
    new_bag = {
        "bag_tag": "BAG-20001",
        "flight": "DL200",
        "origin": "ATL",
        "destination": "LAX"
    }

    response = client.post("/bags", json=new_bag)

    assert response.status_code == 201

    data = response.get_json()
    assert data["message"] == "Bag registered successfully"
    assert data["bag"]["bag_tag"] == "BAG-20001"
    assert data["bag"]["status"] == "Checked In"


# ==========================================
# TEST 5: REJECT DUPLICATE BAG
# ==========================================

def test_duplicate_bag(client):
    duplicate_bag = {
        "bag_tag": "BAG-10045",
        "flight": "DL1254",
        "origin": "ATL",
        "destination": "JFK"
    }

    response = client.post("/bags", json=duplicate_bag)

    assert response.status_code == 409

    data = response.get_json()
    assert data["error"] == "Bag already exists"


# ==========================================
# TEST 6: UPDATE BAG STATUS
# ==========================================

def test_update_bag_status(client):
    response = client.put(
        "/bags/BAG-10045/status",
        json={"status": "Arrived"}
    )

    assert response.status_code == 200

    data = response.get_json()
    assert data["current_status"] == "Arrived"
    assert data["history"][-1]["status"] == "Arrived"


# ==========================================
# TEST 7: REJECT INVALID BAG STATUS
# ==========================================

def test_invalid_bag_status(client):
    response = client.put(
        "/bags/BAG-10045/status",
        json={"status": "Missing"}
    )

    assert response.status_code == 400

    data = response.get_json()
    assert data["error"] == "Invalid baggage status"
