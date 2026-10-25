
from datetime import datetime, timezone
from flask import Flask, request, jsonify

# ==========================================
# INITIALIZE FLASK APPLICATION
# ==========================================

app = Flask(__name__)


# ==========================================
# HELPER: GENERATE UTC TIMESTAMP
# ==========================================

def utc_timestamp():
    return datetime.now(timezone.utc).isoformat()


# ==========================================
# TEMPORARY BAGGAGE DATABASE
# ==========================================

# We will replace this with DynamoDB later.
# Data stored here disappears when Flask restarts.

bags = {
    "BAG-10045": {
        "bag_tag": "BAG-10045",
        "flight": "DL1254",
        "origin": "ATL",
        "destination": "JFK",
        "status": "Loaded",
        "history": [
            {
                "status": "Checked In",
                "timestamp": utc_timestamp()
            },
            {
                "status": "Loaded",
                "timestamp": utc_timestamp()
            }
        ]
    }
}


# ==========================================
# HOME ENDPOINT
# ==========================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "application": "SkyTrack Airline Baggage Tracking",
        "status": "running",
        "message": "Welcome to SkyTrack API"
    }), 200


# ==========================================
# HEALTH CHECK ENDPOINT
# ==========================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "skytrack-api",
        "timestamp": utc_timestamp()
    }), 200


# ==========================================
# GET ALL BAGS
# ==========================================

@app.route("/bags", methods=["GET"])
def get_all_bags():
    return jsonify({
        "total_bags": len(bags),
        "bags": list(bags.values())
    }), 200


# ==========================================
# REGISTER NEW BAG
# ==========================================

@app.route("/bags", methods=["POST"])
def register_bag():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A JSON object is required"
        }), 400

    required_fields = [
        "bag_tag",
        "flight",
        "origin",
        "destination"
    ]

    for field in required_fields:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return jsonify({
                "error": f"{field} is required"
            }), 400

    bag_tag = data["bag_tag"].strip()

    if bag_tag in bags:
        return jsonify({
            "error": "Bag already exists"
        }), 409

    new_bag = {
        "bag_tag": bag_tag,
        "flight": data["flight"].strip(),
        "origin": data["origin"].strip().upper(),
        "destination": data["destination"].strip().upper(),
        "status": "Checked In",
        "history": [
            {
                "status": "Checked In",
                "timestamp": utc_timestamp()
            }
        ]
    }

    bags[bag_tag] = new_bag

    return jsonify({
        "message": "Bag registered successfully",
        "bag": new_bag
    }), 201


# ==========================================
# TRACK BAG BY TAG
# ==========================================

@app.route("/bags/<bag_tag>", methods=["GET"])
def track_bag(bag_tag):
    bag = bags.get(bag_tag)

    if bag is None:
        return jsonify({
            "error": "Bag not found"
        }), 404

    return jsonify({
        "bag_tag": bag["bag_tag"],
        "flight": bag["flight"],
        "origin": bag["origin"],
        "destination": bag["destination"],
        "current_status": bag["status"],
        "history": bag["history"]
    }), 200


# ==========================================
# UPDATE BAG STATUS
# ==========================================

@app.route("/bags/<bag_tag>/status", methods=["PUT"])
def update_bag_status(bag_tag):
    bag = bags.get(bag_tag)

    if bag is None:
        return jsonify({
            "error": "Bag not found"
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A JSON object is required"
        }), 400

    new_status = data.get("status")

    allowed_statuses = [
        "Checked In",
        "Screened",
        "Loaded",
        "In Transit",
        "Arrived",
        "Delivered"
    ]

    if new_status not in allowed_statuses:
        return jsonify({
            "error": "Invalid baggage status",
            "allowed_statuses": allowed_statuses
        }), 400

    bag["status"] = new_status

    bag["history"].append({
        "status": new_status,
        "timestamp": utc_timestamp()
    })

    return jsonify({
        "message": "Baggage status updated",
        "bag_tag": bag_tag,
        "current_status": new_status,
        "history": bag["history"]
    }), 200


# ==========================================
# START FLASK APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
