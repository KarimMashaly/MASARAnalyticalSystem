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

TRAIT_RANGES = {
    "analytical":  (-0.40, 3.30),
    "structure":   (-0.65, 3.10),
    "execution":   (-0.45, 3.35),
    "ambiguity":   (-0.35, 2.00),
    "trial":       (-0.10, 2.50),
    "frustration": (0.00, 1.30),
    "ideation":    (-0.25, 2.10),
    "visual":      (-0.10, 2.50),
    "precision":   (-0.35, 2.60),
    "pattern":     (-0.10, 2.60)
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
        min_v, max_v = TRAIT_RANGES[t]

        norm = (v - min_v) / (max_v - min_v)

        # clamp عشان safety
        norm = max(0.0, min(1.0, norm))

        normalized[t] = round(norm, 3)
    return normalized
