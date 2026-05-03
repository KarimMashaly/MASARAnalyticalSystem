from traits import build_traits, normalize_traits
from scoring import score_tracks, TRACK_PROFILES
from confidence import compute_confidence
from explanation import explain

import json


def read_feature_map(file_path=r"E:\Documents\Masar\Analytical System\MASAR_Analytical_System\Data\feature_map.json"):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_pipeline(answers):
    raw    = build_traits(answers, feature_map=read_feature_map())
    traits = normalize_traits(raw)

    scores          = score_tracks(traits)
    best_track      = max(scores, key=scores.get)  
    confidence_info = compute_confidence(scores)
    explanation     = explain(traits, best_track, scores, confidence_info, TRACK_PROFILES)

    return {
        "traits":      traits,
        "scores":      scores,
        "track":       best_track,
        "confidence":  confidence_info,
        "explanation": explanation
    }

