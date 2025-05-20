import os
import json
from flask import Flask, redirect, jsonify, send_file
from urllib.parse import unquote
from io import BytesIO
import qrcode

app = Flask(__name__)
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"links": {}, "counters": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_qr(code_text):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=4,
    )
    qr.add_data(code_text)
    img = qr.make_image()
    bio = BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio

@app.route("/r/<qr_id>")
def redirect_link(qr_id):
    data = load_data()
    if qr_id not in data["links"]:
        return "QR-код не найден", 404

    data["counters"][qr_id] += 1
    save_data(data)
    return redirect(data["links"][qr_id]["long_url"])

@app.route("/qr/<qr_id>")
def get_qr(qr_id):
    data = load_data()
    if qr_id not in data["links"]:
        return "QR-код не найден", 404

    qr_img = generate_qr(data["links"][qr_id]["short_url"])
    return send_file(qr_img, mimetype="image/png")

@app.route("/stats/<qr_id>")
def get_stats(qr_id):
    data = load_data()
    if qr_id not in data["links"]:
        return jsonify({"error": "QR-код не найден"}), 404

    return jsonify({
        "title": data["links"][qr_id]["title"],
        "short_url": data["links"][qr_id]["short_url"],
        "clicks": data["counters"].get(qr_id, 0)
    })

@app.route("/")
def home():
    return "QR-трекер работает!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
