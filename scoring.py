import json


def read_track_profiles(file_path=r"Data/tracks_profile.json"):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


TRACK_DATA = read_track_profiles()
TRACK_PROFILES = TRACK_DATA["tracks"]


# ----------------------------
# 1) Similarity (محسن)
# ----------------------------
def range_similarity(x, min_val, max_val):
    if min_val <= x <= max_val:
        return 1.0

    # normalize distance relative to range
    range_size = max_val - min_val + 1e-6

    if x < min_val:
        distance = (min_val - x) / range_size
    else:
        distance = (x - max_val) / range_size

    return max(0, 1 - distance)


# ----------------------------
# 2) Base Score
# ----------------------------
def compute_base_score(user, track_data):
    score = 0

    for trait, (min_v, max_v, weight) in track_data["traits"].items():
        sim = range_similarity(user[trait], min_v, max_v)
        score += weight * sim

    return score


# ----------------------------
# 3) Penalty (Dynamic)
# ----------------------------
def compute_penalty(user, track_data):
    penalty = 0

    for rule in track_data.get("penalty_rules", []):
        trait = rule["trait"]
        threshold = rule["threshold"]
        factor = rule["factor"]

        if user[trait] < threshold:
            gap = threshold - user[trait]
            penalty += factor * (gap ** 2)

    return penalty


# ----------------------------
# 4) Interactions (FIXED)
# ----------------------------
def compute_interactions(user, track_data):
    bonus = 0

    for rule in track_data.get("interaction_rules", []):
        traits = rule["traits"]
        thresholds = rule["thresholds"]

        if all(user[t] >= th for t, th in zip(traits, thresholds)):
            bonus += rule["bonus"]

    return bonus


# ----------------------------
# 5) Final Scoring + Confidence
# ----------------------------
def score_tracks(user):
    raw_scores = {}

    for track, data in TRACK_PROFILES.items():
        base = compute_base_score(user, data)
        penalty = compute_penalty(user, data)
        bonus = compute_interactions(user, data)

        final_score = base - penalty + bonus
        raw_scores[track] = final_score

    # normalization
    total = sum(raw_scores.values()) + 1e-6
    normalized_scores = {
        k: round(v / total, 4) for k, v in raw_scores.items()
    }

    # confidence
    sorted_scores = sorted(raw_scores.values(), reverse=True)
    top = sorted_scores[0]
    second = sorted_scores[1] if len(sorted_scores) > 1 else 0

    confidence = (top - second) / (top + 1e-6)

    return {
        "scores": normalized_scores,
        "confidence": round(confidence, 4)
    }