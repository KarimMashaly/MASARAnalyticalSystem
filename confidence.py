import numpy as np 

def compute_confidence(scores: dict) -> dict:

    if len(scores) < 2:
        raise ValueError("Need at least 2 tracks to compute confidence.")

    sorted_items         = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_track,    top    = sorted_items[0]
    second_track, second = sorted_items[1]

    raw_values = np.array(list(scores.values()), dtype=float)

    s_min, s_max = raw_values.min(), raw_values.max()
    score_range  = s_max - s_min

    if score_range < 1e-9:
        return {
            "score":        0.0,
            "label":        "low",
            "top_track":    top_track,
            "second_track": second_track
        }

    scaled = (raw_values - s_min) / score_range

    scaled_sorted        = sorted(zip(scores.keys(), scaled), key=lambda x: x[1], reverse=True)
    _, scaled_top        = scaled_sorted[0]
    _, scaled_second     = scaled_sorted[1]

    # ── Signal 1: gap ─────────────────────────────────────────
    # الفرق بين الأول والثاني هو الـ primary signal
    # 30% فرق = high confidence → نحتاج gap=0.30 يعطي score قريب من 0.85
    # gap مرفوع بـ factor عشان 0.30 → ~0.85
    gap      = scaled_top - scaled_second
    gap_norm = min(1.0, gap * 4)          # 0.30 × 2.8 = 0.84 ✓

    # ── Signal 2: spread ──────────────────────────────────────
    spread      = float(np.std(scaled))
    spread_norm = min(1.0, spread / 0.3)

    # ── Signal 3: ratio_norm ──────────────────────────────────
    ratio      = scaled_top / (scaled_second + 1e-9)
    ratio_norm = min(1.0, (ratio - 1.0) / 1.20)

    # ── Combine ───────────────────────────────────────────────
    confidence = (
        0.60 * gap_norm    +
        0.25 * spread_norm +
        0.15 * ratio_norm
    )
    confidence = round(float(np.clip(confidence, 0.0, 1.0)), 4)

    # ── Label — 0.85 / 0.60 ───────────────────────────────────
    if confidence >= 0.75:
        label = "high"
    elif confidence >= 0.60:
        label = "medium"
    else:
        label = "low"

    return {
        "score":        confidence,
        "label":        label,
        "top_track":    top_track,
        "second_track": second_track
    }