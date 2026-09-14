# -*- coding: utf-8 -*-
"""
example_usage.py - Minimal example showing how to get a prediction from the
trained model, without any web server or CLI involved.

Run from the project root:
    cd career_recommendation_model
    python3 examples/example_usage.py
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import inference

# 1. See what dropdown options a frontend form should offer
options = inference.get_dropdown_options()
print("Available boards:", options["boards"])
print("Available streams:", options["streams"])
print("Available interest domains:", options["domains"])
print()

# 2. A sample student profile
profile = {
    "board": "CBSE",
    "stream": "Science",
    "tenth_percentage": 88,
    "twelfth_percentage": 85,
    "subject_avg": 82,           # average of subject marks + self-rated knowledge
    "exam": "JEE",
    "domains": ["Technology", "Engineering"],
    "soft_leadership": 60,
    "soft_creativity": 70,
    "soft_communication": 65,
    "soft_teamwork": 75,
    "soft_analytical": 85,
    "solo_team_pref": 50,
    "structure_pref": 60,
    "field_desk_pref": 30,
    "risk_tolerance": 55,
}

# 3. Get top-5 career predictions
results = inference.predict_careers(profile, top_k=5)
print("Top 5 career recommendations:")
for i, (career, probability) in enumerate(results, 1):
    print(f"  {i}. {career}  (internal confidence: {probability*100:.1f}%)")
print()

# 4. Get the roadmap/skills/salary info for the top recommendation
top_career = results[0][0]
roadmap = inference.get_roadmap(top_career)
print(f"Roadmap for {top_career}:")
print("  Entrance exam:", roadmap["exam"])
print("  Degree:", roadmap["degree"])
print("  Fresher salary:", roadmap["salary_fresher"])
print("  Experienced salary:", roadmap["salary_experienced"])
