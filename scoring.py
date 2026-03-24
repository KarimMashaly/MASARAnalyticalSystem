# from track_profiles import track_profiles
import json

def read_track_profiles(file_path=r"E:\\Documents\\Masar\\Analytical System\\MASAR_Analytical_System\\Data\\tracks_profile.json"):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
track_profiles = read_track_profiles()
    
def range_similarity(x, min_val, max_val):
    if min_val <= x <= max_val:
        return 1.0

    # penalty per trait 
    if x < min_val:
        return max(0, 1 - (min_val - x) * 3)

    if x > max_val:
        return max(0, 1 - (x - max_val) * 3)
    

def compute_base_score(user_traits, track_data):
    score = 0

    for trait, config in track_data["traits"].items():
        min_v, max_v, weight = config

        sim = range_similarity(user_traits[trait], min_v, max_v)

        score += weight * sim

    return score

def compute_penalty(user, track_data):
    penalty = 0

    for rule in track_data.get("penalty_rules", []):
        trait = rule["trait"]
        threshold = rule["threshold"]
        p = rule["penalty"]

        if user[trait] < threshold:
            gap = threshold - user[trait]
            penalty += p * (gap ** 2)

    return penalty

def compute_interactions(user, track_data):
    bonus = 0

    for rule in track_data.get("interaction_rules", []):
        traits = rule["traits"]
        thresholds = rule["thresholds"]

        for t, th in zip(traits, thresholds):
            if user[t] < th:
                return 0
            else:
                bonus += rule["bonus"]

    return bonus

def score_tracks(user):
    scores = {}

    for track, data in track_profiles.items():
        base = compute_base_score(user, data)
        penalty = compute_penalty(user, data)
        bonus = compute_interactions(user, data)

        final_score = base - penalty + bonus
        scores[track] = round(final_score, 4)

    return scores