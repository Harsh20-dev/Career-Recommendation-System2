"""
Career Recommendation - Interactive CLI
Run this to test the model interactively from a terminal (or Google Colab).
For web/backend integration, use inference.py instead (no input() calls).
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

ART_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model", "artifacts")

# ---------- load everything ----------
model = xgb.XGBClassifier()
model.load_model(f"{ART_DIR}/career_xgb_model.json")
le = joblib.load(f"{ART_DIR}/label_encoder.pkl")
feature_columns = joblib.load(f"{ART_DIR}/feature_columns.pkl")
domain_riasec_map = joblib.load(f"{ART_DIR}/domain_riasec_map.pkl")
meta = joblib.load(f"{ART_DIR}/metadata.pkl")


def ask_choice(prompt, options):
    print(f"\n{prompt}")
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")
    while True:
        raw = input(f"Choose 1-{len(options)} (or type the option name): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        # allow typing the option's name directly (case-insensitive, exact match)
        matches = [o for o in options if o.strip().lower() == raw.lower()]
        if matches:
            return matches[0]
        print("Invalid input, please try again.")


def ask_multi_choice(prompt, options, min_pick=1, max_pick=5):
    print(f"\n{prompt}")
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")
    while True:
        raw = input(f"Enter {min_pick}-{max_pick} numbers separated by commas (e.g. 1,4,7), "
                     f"or type the option names separated by commas: ").strip()
        try:
            parts = [p.strip() for p in raw.split(",") if p.strip()]
            picks = []
            for p in parts:
                if p.isdigit() and 1 <= int(p) <= len(options):
                    picks.append(options[int(p) - 1])
                else:
                    matches = [o for o in options if o.strip().lower() == p.lower()]
                    if matches:
                        picks.append(matches[0])
            picks = list(dict.fromkeys(picks))  # dedupe, keep order
            if min_pick <= len(picks) <= max_pick:
                return picks
        except Exception:
            pass
        print(f"Invalid input. Please give {min_pick} to {max_pick} valid choices.")


def ask_number(prompt, lo=0, hi=100):
    while True:
        raw = input(f"{prompt} ({lo}-{hi}): ").strip()
        try:
            v = float(raw)
            if lo <= v <= hi:
                return v
        except Exception:
            pass
        print(f"Please enter a number between {lo} and {hi}.")


def collect_input():
    print("=" * 60)
    print("CAREER RECOMMENDATION SYSTEM")
    print("=" * 60)

    name = input("\nYour name: ").strip() or "Student"

    board = ask_choice("Your Board:", meta["boards"])
    stream = ask_choice("Your 12th grade Stream:", meta["streams"])

    tenth = ask_number("10th grade percentage", 0, 100)
    twelfth = ask_number("12th grade percentage", 0, 100)

    # subject scores depend on stream (used to compute subject_avg / 'knowledge')
    if stream == "Science":
        combo = ask_choice(
            "Which subject combination do you have in Science?",
            ["PCM (Physics, Chemistry, Maths)", "PCB (Physics, Chemistry, Biology)",
             "PCMB (Physics, Chemistry, Maths, Biology)"],
        )
        if combo.startswith("PCMB"):
            subjects = ["Physics", "Chemistry", "Mathematics", "Biology"]
        elif combo.startswith("PCB"):
            subjects = ["Physics", "Chemistry", "Biology"]
        else:
            subjects = ["Physics", "Chemistry", "Mathematics"]
    else:
        subjects = meta["subjects_by_stream"][stream]

    print(f"\nNow enter your marks (%) in your {stream} stream subjects:")
    subj_scores = [ask_number(f"  {s}", 0, 100) for s in subjects]
    subject_avg = float(np.mean(subj_scores))

    exam = ask_choice("Have you taken any competitive exam?", meta["exams"])
    exam_score = None
    if exam != "None":
        exam_score = ask_number(f"{exam} score/percentile (for reference only, the model doesn't use it directly)", 0, 100)

    print("\n'Knowledge' means your overall understanding of your subjects/field (self-rated):")
    knowledge = ask_number("Rate your overall subject knowledge", 0, 100)
    # blend self-rated knowledge with actual subject marks for a more robust 'subject_avg'
    subject_avg = float(np.mean([subject_avg, knowledge]))

    domains = ask_multi_choice(
        "Which field(s) are you interested in? (pick as many as apply)",
        meta["domains"], min_pick=1, max_pick=6,
    )

    print("\nNow rate your SOFT SKILLS (0 = very low, 100 = very strong):")
    soft_leadership = ask_number("Leadership", 0, 100)
    soft_creativity = ask_number("Creativity", 0, 100)
    soft_communication = ask_number("Communication", 0, 100)
    soft_teamwork = ask_number("Teamwork", 0, 100)
    soft_analytical = ask_number("Analytical / problem-solving", 0, 100)

    print("\nA few quick preferences (0-100 scale):")
    solo_team_pref = ask_number("Prefer working alone (0) or in a team (100)", 0, 100)
    structure_pref = ask_number("Prefer a fixed/structured routine (0) or flexible/creative work (100)", 0, 100)
    field_desk_pref = ask_number("Prefer desk/office work (0) or field/on-ground work (100)", 0, 100)
    risk_tolerance = ask_number("Prefer a stable, safe career (0) or taking risks to try something new (100)", 0, 100)

    return {
        "name": name, "board": board, "stream": stream,
        "tenth_percentage": tenth, "twelfth_percentage": twelfth,
        "marks_avg": (tenth + twelfth) / 2,
        "subject_avg": subject_avg,
        "exam": exam, "exam_score": exam_score,
        "domains": domains,
        "soft_leadership": soft_leadership, "soft_creativity": soft_creativity,
        "soft_communication": soft_communication, "soft_teamwork": soft_teamwork,
        "soft_analytical": soft_analytical,
        "solo_team_pref": solo_team_pref, "structure_pref": structure_pref,
        "field_desk_pref": field_desk_pref, "risk_tolerance": risk_tolerance,
    }


def build_feature_vector(ans):
    row = {c: 0 for c in feature_columns}

    def set_if_present(col):
        if col in row:
            row[col] = 1

    set_if_present(f"stream_{ans['stream']}")
    set_if_present(f"board_{ans['board']}")
    set_if_present(f"competitive_exam_{ans['exam']}")

    row["tenth_percentage"] = ans["tenth_percentage"]
    row["twelfth_percentage"] = ans["twelfth_percentage"]
    row["marks_avg"] = ans["marks_avg"]
    row["subject_avg"] = ans["subject_avg"]

    for c in meta["soft_cols"]:
        key = c.replace("soft_", "soft_")
        row[c] = ans[c]
    for c in meta["pref_cols"]:
        row[c] = ans[c]

    # estimate RIASEC from selected interest domains using training-data averages
    # (domain_riasec_map is a plain dict: {domain: {riasec_col: avg_value}})
    selected = [d for d in ans["domains"] if d in domain_riasec_map]
    if selected:
        for c in meta["riasec_cols"]:
            row[c] = float(np.mean([domain_riasec_map[d][c] for d in selected]))
    else:
        for c in meta["riasec_cols"]:
            row[c] = 0.0

    for d in ans["domains"]:
        col = "domain_" + d.replace(" & ", "_").replace(" ", "_")
        set_if_present(col)

    return pd.DataFrame([row])[feature_columns]


# ---------------------------------------------------------------------------
# REAL-WORLD POPULARITY PRIOR
# ---------------------------------------------------------------------------
# The training dataset over-represents traditional "core" engineering careers
# relative to tech/software careers, which is the OPPOSITE of the real-world
# picture in India: the large majority of engineering students choose CSE/IT
# and its specializations (Software, AI/ML, Data Science, Cybersecurity,
# etc.). Within core engineering itself, real-world popularity also varies a
# lot - ECE/Electrical/Mechanical have large enrollments, while branches like
# Mining/Civil/Structural/Aerospace are chosen by a much smaller fraction of
# students. This dict nudges the model's raw probabilities to better reflect
# that reality. Weight 1.0 = no change; >1.0 = boosted; <1.0 = down-weighted.
TECH_BOOST = 10.0
CORE_KEEP_WEIGHT = 0.5     # ECE / Electrical / Mechanical - still shown, just not dominant
CORE_SUPPRESS_WEIGHT = 0.03  # Mining / Civil / Structural / Aerospace / other niche core branches

CORE_BRANCHES_TO_KEEP = {"Mechanical Engineer", "Electrical Engineer", "Electronics Engineer"}

CATEGORY_POPULARITY_WEIGHT_DEFAULT = {
    "tech_software": TECH_BOOST,
    "medical": 1.0, "science_research": 1.0, "business_finance": 1.0,
    "law_governance": 1.0, "education": 1.0, "social_psych": 1.0,
    "media_creative": 1.0, "design": 1.0, "sports_fitness": 1.0,
    "trades_vocational": 1.0,
}


def _get_weight(career_name, category, tech_engineering_selected):
    if category == "tech_software":
        return TECH_BOOST if tech_engineering_selected else 1.3  # small default tech lean either way
    if category == "engineering_core":
        if not tech_engineering_selected:
            return 0.7  # user showed no engineering/tech interest at all - mild reduction only
        return CORE_KEEP_WEIGHT if career_name in CORE_BRANCHES_TO_KEEP else CORE_SUPPRESS_WEIGHT
    return CATEGORY_POPULARITY_WEIGHT_DEFAULT.get(category, 1.0)


def predict(ans, top_k=5):
    from career_info import CAREER_TO_CATEGORY

    X = build_feature_vector(ans)
    proba = model.predict_proba(X)[0].copy()

    tech_engineering_selected = (
        "Technology" in ans.get("domains", []) or "Engineering" in ans.get("domains", [])
    )

    weights = np.array([
        _get_weight(c, CAREER_TO_CATEGORY.get(c, "business_finance"), tech_engineering_selected)
        for c in le.classes_
    ])
    proba = proba * weights
    proba = proba / proba.sum()

    top_idx = np.argsort(proba)[::-1][:top_k]
    results = [(le.classes_[i], float(proba[i])) for i in top_idx]
    return results


def generate_explanation_and_roadmap(ans, results, top_n=3):
    """Fully offline / rule-based explanation + roadmap for the top predicted
    careers. No external API or internet needed."""
    from career_info import get_career_info

    lines = []

    # ---- why these careers fit (rule-based, from the student's own numbers) ----
    soft_skills = {
        "Leadership": ans["soft_leadership"], "Creativity": ans["soft_creativity"],
        "Communication": ans["soft_communication"], "Teamwork": ans["soft_teamwork"],
        "Analytical": ans["soft_analytical"],
    }
    top_soft = max(soft_skills, key=soft_skills.get)
    top_domains = ", ".join(ans["domains"][:2]) if ans["domains"] else "your chosen interests"

    lines.append("=" * 60)
    lines.append("  WHY THESE CAREERS WERE SUGGESTED")
    lines.append("=" * 60)
    lines.append(
        f"Your strongest soft skill is {top_soft} ({soft_skills[top_soft]:.0f}/100), "
        f"and your interest lies in {top_domains}. Combined with your 12th grade marks "
        f"({ans['twelfth_percentage']:.0f}%) and subject knowledge ({ans['subject_avg']:.0f}/100), "
        f"the model matched this profile most closely with careers in this space."
    )

    # ---- detailed roadmap for each of the top N careers ----
    for rank, (career, prob) in enumerate(results[:top_n], 1):
        info = get_career_info(career)
        lines.append("\n" + "=" * 60)
        lines.append(f"  #{rank}. {career}")
        lines.append("=" * 60)
        lines.append(f"Entrance exam: {info['exam']}")
        lines.append(f"Degree/qualification: {info['degree']}")
        lines.append(f"Average salary - Fresher: {info['salary_fresher']}")
        lines.append(f"Average salary - Experienced: {info['salary_experienced']}")
        lines.append("\nRoadmap:")
        for i, step in enumerate(info["roadmap"], 1):
            lines.append(f"  {i}. {step}")
        lines.append("\nSkills to learn:")
        for sk in info["skills"]:
            lines.append(f"  - {sk}")

    lines.append("\n" + "=" * 60)
    lines.append("Note: Salary figures are approximate India market averages (2026); "
                  "actual pay varies by city, company, and skills.")
    return "\n".join(lines)


def main():
    ans = collect_input()
    results = predict(ans, top_k=5)

    print("\n" + "=" * 60)
    print(f"  {ans['name']}, here are your top career recommendations:")
    print("=" * 60)
    for rank, (career, prob) in enumerate(results, 1):
        print(f"  {rank}. {career}")
    print("=" * 60)
    if ans["exam_score"] is not None:
        print(f"\n(Note: your {ans['exam']} score {ans['exam_score']} is for reference only; "
              f"the training data has no exam-score column, so the model doesn't use it directly.)")

    want_explain = input("\nWant to see a detailed roadmap + skills + salary info? (y/n): ").strip().lower()
    if want_explain == "y":
        print(generate_explanation_and_roadmap(ans, results, top_n=3))


if __name__ == "__main__":
    main()
