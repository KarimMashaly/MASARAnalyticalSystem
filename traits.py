import math

TRAITS_DICTIONARY = {
    "analytical":  0.0,
    "structure":   0.0,
    "execution":   0.0,
    "ambiguity":   0.0,
    "trial":       0.0,
    "frustration": 0.0,
    "ideation":    0.0,
    "precision":   0.0,
    "visual":      0.0,
    "pattern":     0.0
}


def build_traits(answers, feature_map):
    raw = TRAITS_DICTIONARY.copy()

    for q_id, ans in answers.items():
        effects = feature_map[q_id][ans]
        for t, v in effects.items():
            raw[t] += v

    return raw


def normalize_traits(raw):
    """
    Sigmoid normalization with a slightly tighter scaling factor (1.4)
    to keep mid-range scores more separated and preserve signal.
    """
    normalized = {}
    for t, v in raw.items():
        x = v / 1.4
        s = 1 / (1 + math.exp(-x))
        s = max(0.02, min(0.98, s))
        normalized[t] = round(s, 3)
    return normalized
