from traits import build_traits, normalize_traits
from scoring import score_tracks, normalize_scores, TRACK_PROFILES
from confidence import compute_confidence
from explanation import explain

import json


import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def read_feature_map(file_path=None):
    if file_path is None:
        file_path = os.path.join(BASE_DIR, "Data", "feature_map.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_pipeline(answers):
    raw    = build_traits(answers, feature_map=read_feature_map())
    traits = normalize_traits(raw)

    scores          = score_tracks(traits)
    best_track      = max(scores, key=scores.get)
    probs           = normalize_scores(scores)  # softmax
    confidence_info = compute_confidence(probs)
    explanation     = explain(traits, best_track, probs, confidence_info, TRACK_PROFILES)

    return {
        "traits":      traits,
        "scores":      scores,
        "track":       best_track,
        "confidence":  confidence_info,
        "explanation": explanation
    }

