import math

def compute_confidence(probs):
    """
    Robust confidence score using:
    1) Absolute gap (top vs second)
    2) Entropy (distribution uncertainty)
    3) Dominance ratio (top vs total mass)

    probs: dict like {"AI": 0.7, "Backend": 0.2, "Frontend": 0.1}
           (must already be normalized, e.g., via softmax)
    """

    # --- Sort tracks ---
    sorted_items = sorted(probs.items(), key=lambda x: x[1], reverse=True)

    top_track, top_p = sorted_items[0]
    second_track, second_p = sorted_items[1] if len(sorted_items) > 1 else ("", 0.0)

    # --- 1) Absolute gap (primary signal) ---
    gap = top_p - second_p  # [0 → 1]

    # --- 2) Entropy (uncertainty of full distribution) ---
    eps = 1e-9
    entropy = -sum(p * math.log(p + eps) for p in probs.values())

    max_entropy = math.log(len(probs))  # worst case (uniform)
    entropy_norm = entropy / max_entropy  # [0 → 1]
    certainty = 1 - entropy_norm         # invert → higher = better

    # --- 3) Dominance (how much top dominates total mass) ---
    # Helps distinguish 0.5 vs 0.49 vs 0.01 from 0.34/0.33/0.33
    dominance = top_p  # already meaningful since probs sum to 1

    # --- Final combination (weighted) ---
    confidence_raw = (
        (gap * 0.6) +
        (certainty * 0.3) +
        (dominance * 0.1)
    )

    # --- Clamp to [0,1] ---
    confidence = max(0.0, min(1.0, confidence_raw))

    # --- Label ---
    if confidence >= 0.65:
        label = "high"
    elif confidence >= 0.40:
        label = "medium"
    else:
        label = "low"

    return {
        "score": round(confidence, 4),
        "label": label,
        "top_track": top_track,
        "second_track": second_track,
    }