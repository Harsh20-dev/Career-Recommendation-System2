# Career Recommendation Model

An ML-based career recommendation system for students (post-10th/12th, India
context). Given a student's academic marks, competitive exam, interests,
soft skills, and preferences, it predicts the top-matching careers out of
125 options, along with a roadmap, required skills, and average salary
range for each.

## What's in this folder

```
career_recommendation_model/
├── README.md                <- you are here
├── MODEL_CARD.md             <- accuracy, limitations, methodology (read this before deploying)
├── requirements.txt
├── model/
│   └── artifacts/            <- the trained model + everything it needs to run
│       ├── career_xgb_model.json
│       ├── label_encoder.pkl
│       ├── feature_columns.pkl
│       ├── domain_riasec_map.pkl
│       └── metadata.pkl
├── src/
│   ├── inference.py          <- USE THIS to integrate into a backend/website
│   ├── interactive_cli.py    <- terminal/Colab demo (asks questions, prints result)
│   ├── career_info.py        <- roadmap / skills / salary lookup database
│   └── train.py              <- retraining script (only needed if retraining)
├── api/
│   └── app.py                <- example Flask REST API wrapping inference.py
└── examples/
    └── example_usage.py      <- minimal working example, no server needed
```

## Quick start

```bash
pip install -r requirements.txt
cd career_recommendation_model
python3 examples/example_usage.py
```

This loads the trained model and prints a sample prediction - good first
check that everything is set up correctly.

## Integrating into a website/backend

Import `src/inference.py` and call its two functions:

```python
import inference

options = inference.get_dropdown_options()   # for building the input form UI

profile = {
    "board": "CBSE", "stream": "Science",
    "tenth_percentage": 88, "twelfth_percentage": 85, "subject_avg": 82,
    "exam": "JEE", "domains": ["Technology", "Engineering"],
    "soft_leadership": 60, "soft_creativity": 70, "soft_communication": 65,
    "soft_teamwork": 75, "soft_analytical": 85,
    "solo_team_pref": 50, "structure_pref": 60, "field_desk_pref": 30,
    "risk_tolerance": 55,
}
results = inference.predict_careers(profile, top_k=5)   # [(career, confidence), ...]
roadmap = inference.get_roadmap(results[0][0])          # exam/degree/salary/roadmap/skills
```

An example Flask API (`api/app.py`) is included as a working starting point
if the team wants a REST API rather than a direct Python import.

## Retraining (only if needed)

`src/train.py` retrains the model from the original CSV dataset. The
dataset itself is not included in this folder (only needed for retraining,
not for serving predictions) - ask me for it if you need to retrain.

```bash
python3 src/train.py
```

## Please read MODEL_CARD.md before deploying

It documents the model's real accuracy, known limitations, and a manual
correction I applied to counter a real-world/dataset mismatch (see the
"Known limitations" section) - important context for how to present this
to end users responsibly.
