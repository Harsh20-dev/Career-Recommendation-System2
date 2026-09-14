# -*- coding: utf-8 -*-
"""
app.py - Minimal example Flask backend exposing the career model as a REST API.

Run:
    pip install flask flask-cors xgboost scikit-learn pandas numpy joblib
    python3 app.py
Then it's live at http://localhost:5000

Endpoints:
    GET  /api/options          -> dropdown options for the frontend form
    POST /api/predict          -> {profile: {...}} -> top career predictions
    GET  /api/roadmap/<career> -> roadmap/skills/salary for one career

This is a STARTING POINT to build a website UI on top of -
wire these endpoints up to whatever frontend (React, plain HTML+JS, etc.).
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from flask import Flask, request, jsonify
from flask_cors import CORS

import inference

app = Flask(__name__)
CORS(app)  # allow requests from a separate frontend during development


@app.route("/api/options", methods=["GET"])
def options():
    return jsonify(inference.get_dropdown_options())


@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    profile = data.get("profile", {})

    required = [
        "board", "stream", "tenth_percentage", "twelfth_percentage", "subject_avg",
        "soft_leadership", "soft_creativity", "soft_communication",
        "soft_teamwork", "soft_analytical",
        "solo_team_pref", "structure_pref", "field_desk_pref", "risk_tolerance",
    ]
    missing = [f for f in required if f not in profile]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    profile.setdefault("exam", "None")
    profile.setdefault("domains", [])

    top_k = int(data.get("top_k", 5))
    results = inference.predict_careers(profile, top_k=top_k)

    return jsonify({
        "predictions": [
            {"career": career, "match_percent": round(prob * 100, 1)}
            for career, prob in results
        ]
    })


@app.route("/api/roadmap/<career_name>", methods=["GET"])
def roadmap(career_name):
    info = inference.get_roadmap(career_name)
    return jsonify(info)


if __name__ == "__main__":
    # host=0.0.0.0 is required so the app is reachable from outside the
    # container (Render, Railway, Docker, etc.) — 127.0.0.1 only accepts
    # connections from inside the same machine.
    # PORT is injected by most hosting platforms; 5000 is the local fallback.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
