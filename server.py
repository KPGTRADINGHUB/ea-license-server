from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

LICENSE_FILE = "/tmp/licenses.json"

def load_licenses():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_licenses(data):
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f)

@app.route('/validate', methods=['POST'])
def validate():
    data = request.get_json()
    key = data.get("key")
    account_id = data.get("account_id")

    if not key or not account_id:
        return jsonify({"status": "error", "message": "Missing key or account_id"}), 400

    licenses = load_licenses()

    if key not in licenses:
        return jsonify({"status": "invalid"}), 200

    lic = licenses[key]

    if lic.get("used", False):
        return jsonify({"status": "expired"}), 200

    lic["used"] = True
    lic["used_at"] = datetime.now().isoformat()
    lic["account_id"] = account_id
    save_licenses(licenses)

    return jsonify({"status": "ok", "expires_in": lic.get("duration_seconds", 300)}), 200

@app.route('/add_license', methods=['POST'])
def add_license():
    data = request.get_json()
    key = data.get("key")
    duration = data.get("duration_seconds", 300)
    max_uses = data.get("max_uses", 1)

    if not key:
        return jsonify({"status": "error", "message": "Missing key"}), 400

    licenses = load_licenses()
    licenses[key] = {
        "duration_seconds": duration,
        "max_uses": max_uses,
        "created_at": datetime.now().isoformat()
    }
    save_licenses(licenses)
    return jsonify({"status": "added", "key": key}), 200

@app.route('/licenses', methods=['GET'])
def list_licenses():
    licenses = load_licenses()
    return jsonify(licenses), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
