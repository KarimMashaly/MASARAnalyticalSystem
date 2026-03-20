from traits import build_traits, normalize_traits, add_interactions
from scoring import score_tracks
from confidence import compute_confidence
from explanation import explain
import json 



def read_feature_map(file_path=r"Data//feature_map.json"):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    

def run_pipeline(answers):
    raw = build_traits(answers, feature_map=read_feature_map())
    traits = normalize_traits(raw)
    traits = add_interactions(traits)

    scores = score_tracks(traits)
    track = max(scores, key=scores.get)
    confidence = compute_confidence(scores)
    explanation = explain(traits, track)

    return {
        "traits": traits,
        "scores": scores,
        "track": track,
        "confidence": confidence,
        "explanation": explanation
    }