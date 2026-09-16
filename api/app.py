# -*- coding: utf-8 -*-
"""
Flask API for the Career Recommendation System.

Endpoints:
    GET  /                  -> API status and available endpoints
    GET  /health             -> health check
    GET  /api/options        -> dropdown options for the frontend
    POST /api/predict        -> generate career recommendations
    GET  /api/roadmap/<name> -> career roadmap, skills and salary information

Run locally:
    python api/app.py

Production/Render:
    gunicorn --chdir api --bind 0.0.0.0:$PORT app:app
"""

import math
import os
import sys
from typing import Any

# Make the src directory importable when this file is executed from /app/api.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "..", "src")
sys.path.insert(0, SRC_DIR)

from flask import Flask, jsonify, request  # noqa: E402
from flask_cors import CORS  # noqa: E402

import inference  # noqa: E402


app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
CORS(app)


# These fields are required by inference._build_feature_vector().
REQUIRED_FIELDS = [
    "board",
    "stream",
    "tenth_percentage",
    "twelfth_percentage",
    "subject_avg",
    "soft_leadership",
    "soft_creativity",
    "soft_communication",
    "soft_teamwork",
    "soft_analytical",
    "solo_team_pref",
    "structure_pref",
    "field_desk_pref",
    "risk_tolerance",
]

RATING_FIELDS = [
    "tenth_percentage",
    "twelfth_percentage",
    "subject_avg",
    "soft_leadership",
    "soft_creativity",
    "soft_communication",
    "soft_teamwork",
    "soft_analytical",
    "solo_team_pref",
    "structure_pref",
    "field_desk_pref",
    "risk_tolerance",
]


@app.get("/")
def home():
    """Simple homepage so the Render primary URL does not return 404."""
    return jsonify(
        {
            "status": "online",
            "message": "Career Recommendation API is running!",
            "version": "1.0",
            "endpoints": {
                "health": "/health",
                "options": "/api/options",
                "predict": "/api/predict",
                "roadmap": "/api/roadmap/<career_name>",
            },
        }
    )


@app.get("/health")
def health():
    """Health-check endpoint for hosting platforms and monitoring tools."""
    return jsonify({"status": "healthy"})


@app.get("/api/options")
def options():
    """Return the option lists required by the frontend form."""
    try:
        return jsonify(inference.get_dropdown_options())
    except Exception as exc:
        app.logger.exception("Unable to load dropdown options")
        return jsonify({"error": "Unable to load dropdown options", "details": str(exc)}), 500


def _get_json_body() -> dict[str, Any]:
    """Read and validate a JSON request body."""
    if not request.is_json:
        raise ValueError("Request body must be JSON and Content-Type must be application/json")

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")

    return data


def _validate_profile(profile: Any) -> list[str]:
    """Return a list of validation errors for a submitted profile."""
    errors: list[str] = []

    if not isinstance(profile, dict):
        return ["'profile' must be a JSON object"]

    missing = [field for field in REQUIRED_FIELDS if field not in profile]
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")
        return errors

    # Validate string fields.
    if not isinstance(profile["board"], str) or not profile["board"].strip():
        errors.append("'board' must be a non-empty string")
    if not isinstance(profile["stream"], str) or not profile["stream"].strip():
        errors.append("'stream' must be a non-empty string")

    # All score-like fields must be finite numbers from 0 to 100.
    for field in RATING_FIELDS:
        value = profile.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append(f"'{field}' must be a number between 0 and 100")
            continue
        if not math.isfinite(float(value)) or not 0 <= float(value) <= 100:
            errors.append(f"'{field}' must be between 0 and 100")

    # Optional fields.
    if "exam" in profile and not isinstance(profile["exam"], str):
        errors.append("'exam' must be a string")

    if "domains" in profile:
        if not isinstance(profile["domains"], list) or not all(
            isinstance(domain, str) for domain in profile["domains"]
        ):
            errors.append("'domains' must be a list of strings")

    return errors


@app.post("/api/predict")
def predict():
    """Generate the top career recommendations for a student profile."""
    try:
        data = _get_json_body()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    profile = data.get("profile")
    validation_errors = _validate_profile(profile)
    if validation_errors:
        return jsonify({"error": "Invalid profile", "details": validation_errors}), 400

    # Keep defaults compatible with inference.py.
    profile.setdefault("exam", "None")
    profile.setdefault("domains", [])

    try:
        top_k = int(data.get("top_k", 5))
    except (TypeError, ValueError):
        return jsonify({"error": "'top_k' must be an integer"}), 400

    if not 1 <= top_k <= 20:
        return jsonify({"error": "'top_k' must be between 1 and 20"}), 400

    try:
        results = inference.predict_careers(profile, top_k=top_k)
        predictions = [
            {
                "rank": index,
                "career": career,
                "match_percent": round(float(probability) * 100, 1),
            }
            for index, (career, probability) in enumerate(results, start=1)
        ]

        return jsonify(
            {
                "success": True,
                "predictions": predictions,
                "count": len(predictions),
            }
        )
    except Exception as exc:
        app.logger.exception("Prediction failed")
        return jsonify({"error": "Prediction failed", "details": str(exc)}), 500


@app.get("/api/roadmap/<path:career_name>")
def roadmap(career_name: str):
    """Return roadmap, skills and salary information for a career."""
    if not career_name.strip():
        return jsonify({"error": "Career name cannot be empty"}), 400

    try:
        info = inference.get_roadmap(career_name)
        return jsonify({"career": career_name, **info})
    except Exception as exc:
        app.logger.exception("Roadmap lookup failed")
        return jsonify({"error": "Unable to load career roadmap", "details": str(exc)}), 500


# Return JSON instead of Flask's default HTML errors.
@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Route not found", "message": "Please check the requested URL."}), 404


@app.errorhandler(405)
def method_not_allowed(_error):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def internal_server_error(_error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
