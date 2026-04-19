import math

TRAITS_DECTIONATY = {
    "analytical" : 0.0 ,
    "structure" : 0.0 ,
    "execution" : 0.0 ,
    "ambiguity" : 0.0 ,
    "trial" : 0.0 ,
    "frustration" : 0.0 ,
    "ideation" : 0.0 
}
    

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

