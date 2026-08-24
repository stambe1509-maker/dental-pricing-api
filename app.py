"""
Dental Pricing API — Kazanlak & Stara Zagora pilot
Structured pricing data for AI agents / applications.

Run locally:
    python3 app.py
Then visit: http://localhost:5000/api/dental/prices

Endpoints:
    GET /api/dental/clinics
        ?city=kazanlak|stara-zagora   (optional filter)

    GET /api/dental/prices
        ?city=kazanlak|stara-zagora   (optional)
        ?clinic=<clinic_id>           (optional)
        ?service=<search text>        (optional, matches service name, case-insensitive contains)

    GET /api/dental/compare?service=<search text>
        Returns cheapest-to-most-expensive comparison across clinics for a service.

    GET /api/dental/meta
        Basic stats: number of clinics, cities, last updated.
"""

from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "dental_data.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)

CLINICS = DATA["clinics"]
PRICES = DATA["prices"]


@app.route("/api/dental/clinics", methods=["GET"])
def get_clinics():
    city = request.args.get("city")
    results = CLINICS
    if city:
        results = [c for c in results if c["city_slug"] == city]
    return jsonify({"count": len(results), "results": results})


@app.route("/api/dental/prices", methods=["GET"])
def get_prices():
    city = request.args.get("city")
    clinic = request.args.get("clinic")
    service = request.args.get("service")

    results = PRICES
    if city:
        results = [r for r in results if r["city_slug"] == city]
    if clinic:
        results = [r for r in results if r["clinic_id"] == clinic]
    if service:
        needle = service.lower()
        results = [r for r in results if needle in r["service"].lower()]

    return jsonify({"count": len(results), "results": results})


@app.route("/api/dental/compare", methods=["GET"])
def compare_service():
    service = request.args.get("service")
    if not service:
        return jsonify({"error": "Missing required query param: service"}), 400

    needle = service.lower()
    matches = [r for r in PRICES if needle in r["service"].lower()]

    def sort_key(r):
        return r["price_from_bgn"] if r["price_from_bgn"] is not None else float("inf")

    matches_sorted = sorted(matches, key=sort_key)

    return jsonify({
        "query": service,
        "count": len(matches_sorted),
        "cheapest_to_most_expensive": matches_sorted,
    })


@app.route("/api/dental/meta", methods=["GET"])
def meta():
    cities = sorted(set(c["city"] for c in CLINICS))
    return jsonify({
        "total_clinics": len(CLINICS),
        "total_price_records": len(PRICES),
        "cities": cities,
        "pilot_scope": "Dental clinics — Kazanlak and Stara Zagora, Bulgaria",
    })


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "name": "Dental Pricing API — Kazanlak & Stara Zagora pilot",
        "endpoints": [
            "/api/dental/clinics",
            "/api/dental/prices",
            "/api/dental/compare?service=имплант",
            "/api/dental/meta",
        ],
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
