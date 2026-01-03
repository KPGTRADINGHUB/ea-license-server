from flask import Flask, request, jsonify
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Đường dẫn file lưu license (trên Render, dùng ephemeral disk)
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
    data = request.json
    key = data.get("key")
    account_id = data.get("account_id")

    if not key or not account_id:
        return jsonify({"status": "error", "message": "Missing key or account_id"}), 400

    licenses = load_licenses()

    if key not in licenses:
        return jsonify({"status": "invalid"}), 200

    lic = licenses[key]

    # Kiểm tra đã dùng chưa
    if lic.get("used", False):
        return jsonify({"status": "expired"}), 200

    # Ghi nhận đã dùng
    lic["used"] = True
    lic["used_at"] = datetime.now().isoformat()
    lic["account_id"] = account_id
    save_licenses(licenses)

    return jsonify({"status": "ok", "expires_in": lic.get("duration_seconds", 300)}), 200

@app.route('/add_license', methods=['POST'])
def add_license():
    data = request.json
    key = data.get("key")
    duration = data.get("duration_seconds", 300)
    max_uses = data.get("max_uses",
