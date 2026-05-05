import json
import math

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def read_track_profiles(file_path=None):
    if file_path is None:
        file_path = os.path.join(BASE_DIR, "Data", "tracks_profile.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


TRACK_DATA     = read_track_profiles()
TRACK_PROFILES = TRACK_DATA["tracks"]


# ----------------------------
# 1) Similarity
# ----------------------------

def range_similarity(x, min_val, max_val, k=2.0):
    if x >= min_val:
        return 1.0

    distance = min_val - x
    scale = max_val - min_val
    sigma = (scale / k) ** 2

    return math.exp(-(distance ** 2) / sigma)

# ----------------------------
# 2) Base Score
# ----------------------------
def compute_base_score(user, track_data):
    score = 0.0
    for trait, (min_v, max_v, weight) in track_data["traits"].items():
        sim    = range_similarity(user[trait], min_v, max_v)
        score += weight * sim
    return score


# ----------------------------
# 3) Penalty (Dynamic, quadratic)
# ----------------------------
def compute_penalty(user, track_data):
    penalty = 0.0
    for rule in track_data.get("penalty_rules", []):
        trait     = rule["trait"]
        threshold = rule["threshold"]
        factor    = rule["factor"]

        if user[trait] < threshold:
            gap      = threshold - user[trait]
            penalty += factor * (gap ** 2)

    return penalty


# ----------------------------
# 4) Interactions (partial credit)
# ----------------------------
def compute_interactions(user, track_data):
    """
    Full bonus  → all thresholds met.
    50% bonus   → all-but-one met (partial credit — prevents cliff-edge).
    """
    bonus = 0.0

    for rule in track_data.get("interaction_rules", []):
        traits     = rule["traits"]
        thresholds = rule["thresholds"]
        rule_bonus = rule["bonus"]

        hits  = sum(1 for t, th in zip(traits, thresholds) if user[t] >= th)
        total = len(traits)

        if hits == total:
            bonus += rule_bonus
        elif hits == total - 1:
            bonus += rule_bonus * 0.5

    return bonus


# Example Gaussian form:
# similarity = exp(-distance^2 / sigma)
# ----------------------------
# 5) Normalize → [0, 1]
# ----------------------------
def _normalize_scores(raw_scores: dict) -> dict:
    """
    Shift + Scale:
      - Shift  : subtract min  → no negatives, weakest track = 0.0
      - Scale  : divide by max → strongest track = 1.0
      - Ranking and relative gaps are fully preserved.

    Edge case: all tracks equal → return 0.0 for all (no discriminating signal).
    """
    values    = list(raw_scores.values())
    min_score = min(values)
    shifted   = {t: s - min_score for t, s in raw_scores.items()}

    max_shifted = max(shifted.values())
    if max_shifted == 0:
        return {t: 0.0 for t in raw_scores}

    return {t: round(s / max_shifted, 6) for t, s in shifted.items()}


# ----------------------------
# 6) Final Track Scoring
# ----------------------------
def score_tracks(user: dict) -> dict:
    """
    Returns scores in [0, 1].  Best track = 1.0.  All values >= 0.
    Relative ranking is identical to raw scores.
    """
    raw_scores = {}

    for track, data in TRACK_PROFILES.items():
        base    = compute_base_score(user, data)
        penalty = compute_penalty(user, data)
        bonus   = compute_interactions(user, data)

        raw_scores[track] = base - penalty + bonus

    return _normalize_scores(raw_scores)
