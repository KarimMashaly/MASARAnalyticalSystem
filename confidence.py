import math


def compute_confidence(scores):
    """
    Confidence score based on full distribution separation, not just top-second gap.

    Uses a combination of:
    1. Normalized gap between top and second (primary signal)
    2. Distance of third track from top (catches close three-way splits)
    3. Returns a label + numeric score for richer output
    """
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    top_val    = sorted_scores[0][1]
    second_val = sorted_scores[1][1] if len(sorted_scores) > 1 else 0
    third_val  = sorted_scores[2][1] if len(sorted_scores) > 2 else 0

    # Primary: gap between top and second, normalized by total range
    score_range = top_val - third_val + 1e-6
    gap_ratio = (top_val - second_val) / score_range

    # Secondary: how far second is from third (spread of the pack)
    pack_spread = (second_val - third_val) / score_range

    confidence_raw = (gap_ratio * 0.75) + (pack_spread * 0.25)
    confidence = round(min(1.0, max(0.0, confidence_raw)), 4)

    # Label for explanation engine
    if confidence >= 0.55:
        label = "high"
    elif confidence >= 0.25:
        label = "medium"
    else:
        label = "low"

    return {
        "score": confidence,
        "label": label,
        "top_track": sorted_scores[0][0],
        "second_track": sorted_scores[1][0]
    }
