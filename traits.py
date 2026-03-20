import math
import json

def read_traits(file_path=r"Data//traits.json"):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
TRAITS_DECTIONATY = read_traits()

def build_traits(answers, feature_map):
    raw = TRAITS_DECTIONATY.copy()

    for q_id, ans in answers.items():
        effects = feature_map[q_id][ans]
        for t, v in effects.items():
            raw[t] += v

    return raw


def normalize_traits(raw):
    normalized = {}
    for t, v in raw.items():
        x = v / 1.2
        s = 1 / (1 + math.exp(-x))
        s = max(0.02, min(0.98, s))
        normalized[t] = round(s, 3)
    return normalized


def add_interactions(traits):
    traits["ai_signal"] = traits["analytical"] * traits["ambiguity"]
    traits["backend_signal"] = traits["analytical"] * traits["structure"]
    traits["frontend_signal"] = traits["execution"] * traits["trial"]
    return traits