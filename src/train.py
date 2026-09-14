"""
Career Recommendation Model - Training Script
Trains an XGBoost multiclass classifier on career_dataset_v3.csv

Run: python3 train.py
Outputs (saved in ./artifacts/):
    career_xgb_model.json      -> trained XGBoost model
    label_encoder.pkl          -> encodes/decodes the 125 career labels
    feature_columns.pkl        -> exact column order the model expects
    domain_riasec_map.pkl      -> avg RIASEC profile per interest-domain (for inference)
    metadata.pkl               -> lists of streams/boards/exams/domains/subjects for the UI
"""

import json
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, top_k_accuracy_score, classification_report
import xgboost as xgb

DATA_PATH = "career_dataset_v3.csv"
OUT_DIR = "artifacts"
os.makedirs(OUT_DIR, exist_ok=True)

ALL_DOMAINS = [
    "Agriculture & Environment", "Business", "Design & Creative", "Education",
    "Engineering", "Healthcare", "Law & Governance", "Media & Communication",
    "Science & Research", "Social Impact", "Sports & Fitness", "Technology",
    "Trades & Hands-on",
]

SUBJECTS_BY_STREAM = {
    "Commerce": ["Accountancy", "Economics", "Business Studies"],
    "Science": ["Physics", "Chemistry", "Mathematics"],
    "Arts": ["History", "Political Science", "Geography"],
    "Vocational": ["Trade Theory", "Trade Practical", "Workshop Science"],
}

RIASEC_COLS = ["riasec_R", "riasec_I", "riasec_A", "riasec_S", "riasec_E", "riasec_C"]
SOFT_COLS = ["soft_leadership", "soft_creativity", "soft_communication",
             "soft_teamwork", "soft_analytical"]
PREF_COLS = ["solo_team_pref", "structure_pref", "field_desk_pref", "risk_tolerance"]


def load_and_prepare(path):
    df = pd.read_csv(path)

    # IMPORTANT: force plain python 'object' dtype for all string columns.
    # Newer pandas can read CSVs into the pandas-native StringDtype, which is
    # NOT reliably unpicklable across different pandas/sklearn versions
    # (e.g. this breaks when a model trained on pandas 2.x is loaded on
    # Google Colab's older pandas/sklearn). Plain object-dtype strings
    # pickle safely everywhere.
    for col in df.columns:
        if str(df[col].dtype) in ("string", "string[python]", "string[pyarrow]") or df[col].dtype == object:
            df[col] = df[col].astype(object).where(df[col].notna(), None)
            df[col] = df[col].apply(lambda x: str(x) if x is not None else x)

    df["competitive_exam"] = df["competitive_exam"].fillna("None")

    # multi-hot encode interest domains
    def parse_domains(x):
        try:
            return json.loads(x)
        except Exception:
            return []

    domain_lists = df["interest_domains_json"].apply(parse_domains)
    for d in ALL_DOMAINS:
        col = "domain_" + d.replace(" & ", "_").replace(" ", "_")
        df[col] = domain_lists.apply(lambda lst: 1 if d in lst else 0)

    return df, domain_lists


def build_domain_riasec_map(df, domain_lists):
    """For each interest domain, compute the average RIASEC profile of students
    who selected it. Used at inference time to *estimate* RIASEC scores from a
    user's chosen interest domains, since end users won't know their RIASEC code.
    Returned as a plain nested dict (domain -> {riasec_col: float}) rather than
    a DataFrame, so it pickles/unpickles safely across pandas versions."""
    rows = []
    for domains, (_, r) in zip(domain_lists, df.iterrows()):
        for d in domains:
            rows.append({**{c: float(r[c]) for c in RIASEC_COLS}, "domain": d})
    tmp = pd.DataFrame(rows)
    domain_map_df = tmp.groupby("domain")[RIASEC_COLS].mean()
    domain_map = {
        str(domain): {str(c): float(v) for c, v in row.items()}
        for domain, row in domain_map_df.to_dict(orient="index").items()
    }
    return domain_map


def main():
    df, domain_lists = load_and_prepare(DATA_PATH)
    domain_riasec_map = build_domain_riasec_map(df, domain_lists)

    domain_cols = ["domain_" + d.replace(" & ", "_").replace(" ", "_") for d in ALL_DOMAINS]

    numeric_cols = (
        ["tenth_percentage", "twelfth_percentage", "marks_avg", "subject_avg"]
        + SOFT_COLS + PREF_COLS + RIASEC_COLS
    )
    categorical_cols = ["stream", "board", "competitive_exam"]

    X = pd.get_dummies(df[categorical_cols], prefix=categorical_cols)
    X[numeric_cols] = df[numeric_cols]
    X[domain_cols] = df[domain_cols]

    feature_columns = list(X.columns)

    le = LabelEncoder()
    y = le.fit_transform(df["label"].astype(str).tolist())
    le.classes_ = np.array([str(c) for c in le.classes_])

    from sklearn.utils.class_weight import compute_sample_weight

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )

    # The dataset is heavily imbalanced (e.g. Mechanical Engineer: 715 samples vs
    # Software Engineer: 200 samples). Without correction, XGBoost's overall-accuracy
    # objective leans toward the majority classes whenever the input features are
    # ambiguous. Balanced sample weights (inverse class frequency) counteract this.
    sample_weight = compute_sample_weight(class_weight="balanced", y=y_train)

    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.15,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="multi:softprob",
        num_class=len(le.classes_),
        eval_metric="mlogloss",
        tree_method="hist",
        n_jobs=-1,
        random_state=42,
        early_stopping_rounds=20,
    )

    print("Training started...")
    model.fit(X_train, y_train, sample_weight=sample_weight,
              eval_set=[(X_test, y_test)], verbose=False)
    print("Training done. Best iteration:", model.best_iteration)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    acc = accuracy_score(y_test, y_pred)
    top3 = top_k_accuracy_score(y_test, y_proba, k=3, labels=np.arange(len(le.classes_)))
    top5 = top_k_accuracy_score(y_test, y_proba, k=5, labels=np.arange(len(le.classes_)))

    print(f"Test accuracy (top-1): {acc:.4f}")
    print(f"Test accuracy (top-3): {top3:.4f}")
    print(f"Test accuracy (top-5): {top5:.4f}")

    # save artifacts
    model.save_model(os.path.join(OUT_DIR, "career_xgb_model.json"))
    joblib.dump(le, os.path.join(OUT_DIR, "label_encoder.pkl"))
    joblib.dump(feature_columns, os.path.join(OUT_DIR, "feature_columns.pkl"))
    joblib.dump(domain_riasec_map, os.path.join(OUT_DIR, "domain_riasec_map.pkl"))

    metadata = {
        "streams": sorted(df["stream"].unique().tolist()),
        "boards": sorted(df["board"].unique().tolist()),
        "exams": sorted(df["competitive_exam"].unique().tolist()),
        "domains": ALL_DOMAINS,
        "subjects_by_stream": SUBJECTS_BY_STREAM,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "domain_cols": domain_cols,
        "soft_cols": SOFT_COLS,
        "pref_cols": PREF_COLS,
        "riasec_cols": RIASEC_COLS,
        "test_accuracy_top1": float(acc),
        "test_accuracy_top3": float(top3),
        "test_accuracy_top5": float(top5),
        "n_classes": int(len(le.classes_)),
    }
    joblib.dump(metadata, os.path.join(OUT_DIR, "metadata.pkl"))
    with open(os.path.join(OUT_DIR, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print("\nSaved artifacts to ./artifacts/")
    print("\nTop 15 most important features:")
    importances = model.feature_importances_
    order = np.argsort(importances)[::-1][:15]
    for i in order:
        print(f"  {feature_columns[i]:35s} {importances[i]:.4f}")


if __name__ == "__main__":
    main()
