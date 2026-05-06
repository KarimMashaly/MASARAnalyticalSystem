import numpy as np


def compute_confidence(scores: dict) -> dict:
    """
    Computes how decisively one track leads over all others.

    Expects scores in [0, 1] with best track = 1.0  (output of score_tracks).

    Three independent signals, each in [0, 1]:
      1. gap        — absolute distance between top and second  → in [0, 1]
      2. ratio_norm — how many times better top is vs second    → in [0, 1]
      3. spread     — how spread apart ALL tracks are           → in [0, 1]

    Weights:
      gap    0.50  — primary: clearest single indicator of separation
      spread 0.30  — secondary: captures full-field dispersion
      ratio  0.20  — tertiary: relative contrast (correlated with gap, so lower weight)
    """

    if len(scores) < 2:
        raise ValueError("Need at least 2 tracks to compute confidence.")

    values = np.array(list(scores.values()), dtype=float)

    # --- sort ---
    sorted_items          = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_track,    top     = sorted_items[0]
    second_track, second  = sorted_items[1]

    # -----------------------------------------------------------
    # Signal 1: gap  (already in [0, 1] because scores ∈ [0, 1])
    # -----------------------------------------------------------
    gap = top - second                          # ∈ [0, 1]

    # -----------------------------------------------------------
    # Signal 2: ratio_norm
    # ratio = top / second  ∈ [1, ∞)
    # Map linearly: ratio=1 → 0.0,  ratio=3 → 1.0, clamp above 3
    # Formula: (ratio - 1) / 2   clamped to [0, 1]
    # -----------------------------------------------------------
    ratio      = top / (second + 1e-9)
    ratio_norm = min(1.0, (ratio - 1.0) / 2.0)

    # -----------------------------------------------------------
    # Signal 3: spread — std of ALL tracks, normalized by range
    # range = max - min = 1 - 0 = 1  (guaranteed after shift+scale)
    # so spread_norm = std(values) directly, clamped to [0, 1]
    # -----------------------------------------------------------
    spread      = float(np.std(values))
    spread_norm = min(1.0, spread)

    # --- combine ---
    confidence = (
        0.50 * gap        +
        0.30 * spread_norm +
        0.20 * ratio_norm
    )

    confidence = round(float(np.clip(confidence, 0.0, 1.0)), 4)

    # --- label ---
    if confidence >= 0.70:
        label = "high"
    elif confidence >= 0.40:
        label = "medium"
    else:
        label = "low"

    return {
        "score":        confidence,
        "label":        label,
        "top_track":    top_track,
        "second_track": second_track,
    }
