"""
app.py — backend minimal untuk TKA IX-F.

Fungsinya sekarang cuma satu: menerima hasil tes dari frontend dan
menyimpannya sebagai backup di folder data/ (satu file JSON per submission).
Ini BUKAN sistem autentikasi atau database asli — itu tahap berikutnya
kalau proyeknya sudah butuh akun siswa sungguhan.

Praktik keamanan yang sudah dipasang di sini:
- Input divalidasi & di-whitelist (level cuma boleh salah satu dari 3 nilai)
- Nama file dibuat sendiri oleh server (uuid), TIDAK pernah dari input user
  -> mencegah path traversal (mis. "../../etc/passwd")
- Ukuran body request dibatasi
- CORS dibatasi ke origin yang eksplisit diizinkan (isi ORIGIN_DIIZINKAN)
- Tidak ada secret / API key yang ditulis langsung di kode ini

Yang BELUM ada dan wajib ditambah sebelum dipakai publik/production:
- HTTPS (pakai reverse proxy seperti nginx / Caddy, jangan http:// polos)
- Rate limiting per-IP (mis. pakai Flask-Limiter) supaya endpoint ini tidak
  bisa dibanjiri
- Autentikasi kalau nanti ada akun siswa
- Backup data yang lebih tahan lama (bukan cuma file JSON lokal) --
  misalnya sinkron berkala ke penyimpanan terpisah
"""

import json
import os
import re
import uuid
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_from_directory

# Folder frontend ada satu tingkat di atas backend/ (index.html, css/, js/)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
# static_folder=None: kita atur sendiri route statisnya di bawah, supaya
# folder backend/ (source code + data/ hasil siswa) TIDAK ikut ter-expose.
app = Flask(__name__, static_folder=None)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Ganti dengan domain asli kamu waktu deploy. Jangan pakai "*" di production.
ORIGIN_DIIZINKAN = os.environ.get("ORIGIN_DIIZINKAN", "http://localhost:5000")

LEVEL_VALID = {"acak", "smp", "sma"}
STATUS_VALID = {"tes-dimulai", "tes-selesai"}

# Batasi ukuran body request (mis. 10 KB) supaya tidak disalahgunakan
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024


@app.after_request
def tambah_header_keamanan(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Access-Control-Allow-Origin"] = ORIGIN_DIIZINKAN
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def validasi_payload(data):
    """Validasi ketat: tolak apa pun yang tidak sesuai bentuk yang diharapkan."""
    if not isinstance(data, dict):
        return False, "Body harus berupa objek JSON."

    level = data.get("level")
    if level not in LEVEL_VALID:
        return False, "Field 'level' tidak valid."

    status = data.get("status")
    if status not in STATUS_VALID:
        return False, "Field 'status' tidak valid."

    waktu = data.get("waktu")
    if not isinstance(waktu, str) or not re.match(r"^\d{4}-\d{2}-\d{2}T", waktu):
        return False, "Field 'waktu' harus format ISO 8601."

    return True, None


@app.route("/api/hasil-tes", methods=["POST", "OPTIONS"])
def simpan_hasil_tes():
    if request.method == "OPTIONS":
        # preflight CORS
        return "", 204

    data = request.get_json(silent=True)
    valid, pesan_error = validasi_payload(data)
    if not valid:
        return jsonify({"ok": False, "error": pesan_error}), 400

    entri = {
        "level": data["level"],
        "status": data["status"],
        "waktu_klien": data["waktu"],
        "waktu_server": datetime.now(timezone.utc).isoformat(),
    }

    # Nama file dibuat server-side (uuid), bukan dari input -> aman dari path traversal
    nama_file = f"{uuid.uuid4().hex}.json"
    path_file = os.path.join(DATA_DIR, nama_file)
    with open(path_file, "w", encoding="utf-8") as f:
        json.dump(entri, f, ensure_ascii=False, indent=2)

    return jsonify({"ok": True, "id": nama_file}), 201


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"ok": True, "layanan": "TKA IX-F backend"}), 200


@app.route("/", methods=["GET"])
def beranda():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path_file>", methods=["GET"])
def file_statis(path_file):
    # PENTING: whitelist folder yang boleh diakses publik. Ini mencegah orang
    # buka /backend/app.py atau /backend/data/<file>.json lewat browser --
    # tanpa batas ini, seluruh folder project (termasuk hasil tes siswa lain)
    # bisa diintip lewat URL.
    if not path_file.startswith(("css/", "js/")):
        return jsonify({"ok": False, "error": "Tidak ditemukan."}), 404
    return send_from_directory(FRONTEND_DIR, path_file)


if __name__ == "__main__":
    # debug=False secara default -- JANGAN nyalakan debug=True di production,
    # karena itu bisa membocorkan source code lewat halaman error.
    app.run(host="127.0.0.1", port=5000, debug=False)
