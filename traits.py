import math

TRAIT_DEFINITION = {
    "analytical": "logical step-by-step reasoning",
    "pattern": "ability to detect hidden relationships and generalize",
    "precision": "attention to correctness, edge cases, strict validation",
    "structure": "preference for order, planning, deterministic flow",
    "execution": "drive to build and complete working solutions",
    "trial": "willingness to try without full understanding",
    "ambiguity": "comfort working without clear requirements",
    "ideation": "ability to generate ideas and alternatives",
    "visual": "sensitivity to UI/UX and visual clarity",
    "frustration": "persistence under repeated failure"
}

TRAIT_RULES = {
    "analytical": "used only when breaking problem into steps",
    "pattern": "used only when detecting relations or abstraction",
    "precision": "used only for correctness, edge cases, validation",
    "structure": "used only for planning/order (NOT thinking)",
    "execution": "used only for acting/building",
    "trial": "used only when action happens WITHOUT full understanding",
    "ambiguity": "used when user accepts unclear situations",
    "ideation": "used when generating ideas (not implementing)",
    "visual": "used only for UI/UX perception",
    "frustration": "used when continuing despite failure"
}

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


def compute_trial(execution, ambiguity, analytical, precision, structure):
    """
    All inputs expected in range [0, 1]
    Returns trial in range (0, 1)
    """

    # --- 1) Interaction core ---
    core = execution * ambiguity

    # --- 2) Conditional blocks (only if they hinder execution) ---
    analytical_block = max(0.0, analytical - execution)
    precision_block  = max(0.0, precision  - execution)

    # --- 3) Logit (z) ---
    z = (
        -1.2
        + 3.0 * core
        - 0.8 * structure
        - 0.6 * analytical_block
        - 0.5 * precision_block
    )

    # --- 4) Sigmoid → (0, 1) ---
    trial = 1.0 / (1.0 + math.exp(-z))

    return trial


def build_traits(answers, feature_map):
    raw = TRAITS_DICTIONARY.copy()

    for q_id, ans in answers.items():
        effects = feature_map[q_id][ans]
        for t, v in effects.items():
            raw[t] += v
    
    raw["trial"] = compute_trial(raw["execution"], raw["ambiguity"], raw["analytical"], raw["precision"], raw["structure"])
   
    return raw



def normalize_traits(raw):
    """
    Sigmoid normalization with a slightly tighter scaling factor (1.4)
    to keep mid-range scores more separated and preserve signal.
    """
    normalized = {}
    for t, v in raw.items():

        # --- skip trial (already normalized) ---
        if t == "trial":
            normalized[t] = round(v, 3)
            continue

        min_v, max_v = TRAIT_RANGES[t]

        norm = (v - min_v) / (max_v - min_v)

        # clamp عشان safety
        norm = max(0.0, min(1.0, norm))
        normalized[t] = round(norm, 3)

    return normalized
