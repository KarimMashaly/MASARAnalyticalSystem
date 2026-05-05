import numpy as np

def compute_confidence(scores):
    values = np.array(list(scores.values()))
    
    # --- sort ---
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_track, top = sorted_items[0]
    second_track, second = sorted_items[1]

    # --- signals ---
    gap = top - second
    
    ratio = top / (second + 1e-9)
    ratio_norm = min(1.0, (ratio - 1) / (ratio + 1e-9)) 
    # 1 → 0 , 3 → 1

    spread = np.std(values)
    spread_norm = spread / (np.max(values) + 1e-9)
    spread_norm = min(1.0, spread_norm)  
    # adjustable

    # --- combine ---
    confidence = (
        0.5 * gap +
        0.3 * ratio_norm +
        0.2 * spread_norm
    )

    confidence = max(0.0, min(1.0, confidence))

    # --- label ---
    if confidence >= 0.60:
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