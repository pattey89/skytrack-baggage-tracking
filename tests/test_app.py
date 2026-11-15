
from app import app


# ==========================================
# TEST 1: HEALTH CHECK ENDPOINT
# ==========================================

def test_health_check():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"


# ==========================================
# TEST 2: TRACK EXISTING BAG
# ==========================================

def test_track_existing_bag():
    client = app.test_client()

    response = client.get("/bags/BAG-10045")

    assert response.status_code == 200

    data = response.get_json()

    assert data["bag_tag"] == "BAG-10045"
    assert data["flight"] == "DL1254"
    assert data["current_status"] == "Loaded"


# ==========================================
# TEST 3: TRACK NONEXISTENT BAG
# ==========================================

def test_track_nonexistent_bag():
    client = app.test_client()

    response = client.get("/bags/BAG-99999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Bag not found"
