# Model Card - Career Recommendation Model

## Summary

- **Task**: Multi-class classification - predict the best-matching career(s)
  out of 125 possible careers, given a student's profile.
- **Model**: XGBoost (gradient-boosted decision trees), trained with
  class-balanced sample weights.
- **Training data**: 33,257 synthetic student profiles, 125 career labels,
  26 features (marks, stream, board, competitive exam, interests, soft
  skills, preferences, RIASEC personality scores).

## Performance

| Metric | Score |
|---|---|
| Top-1 accuracy | ~23-24% |
| Top-3 accuracy | ~49% |
| Top-5 accuracy | ~63% |

For context: random guessing across 125 classes would score ~0.8%, so the
model is clearly learning real signal - but with 125 possible careers, a
single "correct" answer is a hard target, and top-1 accuracy alone
understates how useful the model is. **The product should present the
top-3 to top-5 results as a set of options to explore, not a single
definitive answer.**

## Training data - important caveat

The dataset is **synthetic** (generated, not collected from real students'
actual outcomes). This means:
- The feature-label relationships the model learned reflect whatever logic
  generated the dataset, not verified real-world outcomes.
- Before using this in front of real students at any meaningful scale, it
  would be valuable to validate/replace with real outcome data if
  available, or at least track live user feedback (see "Recommendations"
  below).

## Known limitation: dataset vs. real-world popularity mismatch, and the fix applied

The training dataset over-represents traditional "core" engineering careers
(e.g. Mining Engineer, Structural Engineer - 400-600 samples each) relative
to tech/software careers (e.g. Software Engineer, Data Scientist - ~200-225
samples each). This is the **opposite** of real-world career popularity in
India, where CSE/IT and its specializations are the most commonly pursued
engineering path by a large margin.

**Fix applied**: `src/inference.py` and `src/interactive_cli.py` apply a
manual post-processing weight to the model's raw output probabilities when
a student expresses interest in Engineering and/or Technology - boosting
tech/software careers and down-weighting niche core-engineering branches,
while keeping widely-pursued core branches (Mechanical, Electrical,
Electronics) present at a moderate level. This is a **deliberate, hand-tuned
business-logic correction**, not something the model learned on its own -
documented in the `_get_weight()` function and its surrounding comments in
`inference.py`. It was tuned by testing a handful of representative
profiles, not validated against a held-out real-world dataset.

**Why this matters for you to know**: this correction improves real-world
relevance based on general knowledge of India's engineering career
landscape, but it is a heuristic override, not a data-driven fix. The
principled long-term fix is a real (or better-calibrated) dataset that
reflects actual career-choice distributions, removing the need for a manual
correction entirely.

## Intended use

- A "career exploration" tool that surfaces possibilities a student might
  not have considered, alongside a roadmap and salary context for each.
- **Not** intended as a definitive, singular "this is your career" answer.
  Recommend pairing with a disclaimer and/or access to a human counselor.

## Recommendations for production use

1. Present results as a set of options ("careers to explore"), not a single
   verdict - especially given the ~23% top-1 accuracy.
2. Log predictions and (if possible) collect lightweight user feedback
   ("was this relevant? yes/no") to build a real-world evaluation set over
   time.
3. Revisit the manual popularity-correction weights periodically, or replace
   them with a data-driven fix once real usage data is available.
4. Retrain periodically as more/better data becomes available (`src/train.py`).
