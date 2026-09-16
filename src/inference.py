# -*- coding: utf-8 -*-
"""
inference.py - Deployment-ready career prediction module (NO input()/CLI code).

This is what a backend (Flask/FastAPI/Django/Node-via-subprocess/etc.) should
import. It loads the trained model once, and exposes two plain functions:

    predict_careers(profile: dict, top_k: int = 5) -> list[(career, probability)]
    get_roadmap(career_name: str) -> dict (exam, degree, salary, roadmap, skills)

Required files alongside this script (all inside the `artifacts/` folder):
    artifacts/career_xgb_model.json
    artifacts/label_encoder.pkl
    artifacts/feature_columns.pkl
    artifacts/domain_riasec_map.pkl
    artifacts/metadata.pkl
Plus `career_info.py` in the same folder (roadmap/skills/salary database).

The original CSV dataset is NOT required for inference - only for retraining.
"""

import os
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from career_info import CAREER_TO_CATEGORY, get_career_info

ART_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model", "artifacts")

# ---- load once at import time (do this once per server process, not per-request) ----
_model = xgb.XGBClassifier()
_model.load_model(os.path.join(ART_DIR, "career_xgb_model_small.ubj"))
_le = joblib.load(os.path.join(ART_DIR, "label_encoder.pkl"))
_feature_columns = joblib.load(os.path.join(ART_DIR, "feature_columns.pkl"))
_domain_riasec_map = joblib.load(os.path.join(ART_DIR, "domain_riasec_map.pkl"))
_meta = joblib.load(os.path.join(ART_DIR, "metadata.pkl"))

# Real-world popularity correction (see career_info.py comment for rationale):
# the training dataset over-represents traditional core-engineering careers
# relative to tech/software careers compared to real-world India demand, and
# within core engineering, niche branches (Mining/Civil/Structural/Aerospace)
# are also over-represented relative to how many students actually pursue them.
_TECH_BOOST = 10.0
_CORE_KEEP_WEIGHT = 0.5
_CORE_SUPPRESS_WEIGHT = 0.03
_CORE_BRANCHES_TO_KEEP = {"Mechanical Engineer", "Electrical Engineer", "Electronics Engineer"}


def _get_weight(career_name, category, tech_engineering_selected):
    if category == "tech_software":
        return _TECH_BOOST if tech_engineering_selected else 1.3
    if category == "engineering_core":
        if not tech_engineering_selected:
            return 0.7
        return _CORE_KEEP_WEIGHT if career_name in _CORE_BRANCHES_TO_KEEP else _CORE_SUPPRESS_WEIGHT
    return 1.0


def get_dropdown_options():
    """Returns the option lists the frontend needs to render dropdowns/checkboxes."""
    return {
        "boards": _meta["boards"],
        "streams": _meta["streams"],
        "exams": _meta["exams"],
        "domains": _meta["domains"],
        "subjects_by_stream": _meta["subjects_by_stream"],
    }


def _build_feature_vector(profile):
    """profile is a dict - see predict_careers() docstring for the exact schema."""
    row = {c: 0 for c in _feature_columns}

    def set_if_present(col):
        if col in row:
            row[col] = 1

    set_if_present(f"stream_{profile['stream']}")
    set_if_present(f"board_{profile['board']}")
    set_if_present(f"competitive_exam_{profile.get('exam', 'None')}")

    row["tenth_percentage"] = profile["tenth_percentage"]
    row["twelfth_percentage"] = profile["twelfth_percentage"]
    row["marks_avg"] = (profile["tenth_percentage"] + profile["twelfth_percentage"]) / 2
    row["subject_avg"] = profile["subject_avg"]

    for c in _meta["soft_cols"]:
        row[c] = profile[c]
    for c in _meta["pref_cols"]:
        row[c] = profile[c]

    domains = profile.get("domains", [])
    selected = [d for d in domains if d in _domain_riasec_map]
    if selected:
        for c in _meta["riasec_cols"]:
            row[c] = float(np.mean([_domain_riasec_map[d][c] for d in selected]))
    else:
        for c in _meta["riasec_cols"]:
            row[c] = 0.0

    for d in domains:
        col = "domain_" + d.replace(" & ", "_").replace(" ", "_")
        set_if_present(col)

    return pd.DataFrame([row])[_feature_columns]


def predict_careers(profile, top_k=5):
    """
    profile: dict with keys:
        board: str                    (one of get_dropdown_options()['boards'])
        stream: str                   (one of get_dropdown_options()['streams'])
        tenth_percentage: float (0-100)
        twelfth_percentage: float (0-100)
        subject_avg: float (0-100)    (avg of stream subject marks + self-rated knowledge)
        exam: str                     (one of get_dropdown_options()['exams'], or "None")
        domains: list[str]            (subset of get_dropdown_options()['domains'])
        soft_leadership, soft_creativity, soft_communication,
        soft_teamwork, soft_analytical: float (0-100)
        solo_team_pref, structure_pref, field_desk_pref, risk_tolerance: float (0-100)

    Returns: list of (career_name: str, probability: float) tuples, sorted
             highest-probability first, length top_k.
    """
    X = _build_feature_vector(profile)
    proba = _model.predict_proba(X)[0].copy()

    tech_engineering_selected = (
        "Technology" in profile.get("domains", []) or "Engineering" in profile.get("domains", [])
    )
    weights = np.array([
        _get_weight(c, CAREER_TO_CATEGORY.get(c, "business_finance"), tech_engineering_selected)
        for c in _le.classes_
    ])
    proba = proba * weights
    proba = proba / proba.sum()

    top_idx = np.argsort(proba)[::-1][:top_k]
    return [(str(_le.classes_[i]), float(proba[i])) for i in top_idx]


def get_roadmap(career_name):
    """Returns {exam, degree, salary_fresher, salary_experienced, roadmap: [...], skills: [...]}"""
    return get_career_info(career_name)


if __name__ == "__main__":
    # quick self-test when run directly: python3 inference.py
    sample_profile = {
        "board": "CBSE", "stream": "Science",
        "tenth_percentage": 88, "twelfth_percentage": 85, "subject_avg": 82,
        "exam": "JEE", "domains": ["Technology", "Engineering"],
        "soft_leadership": 60, "soft_creativity": 70, "soft_communication": 65,
        "soft_teamwork": 75, "soft_analytical": 85,
        "solo_team_pref": 50, "structure_pref": 60, "field_desk_pref": 30, "risk_tolerance": 55,
    }
    results = predict_careers(sample_profile, top_k=5)
    print("Top 5 predictions:")
    for career, prob in results:
        print(f"  {career}: {prob*100:.1f}%")
    print("\nRoadmap for #1:", get_roadmap(results[0][0])["exam"])
