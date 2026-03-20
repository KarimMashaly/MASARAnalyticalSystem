def compute_confidence(scores):
    sorted_scores = sorted(scores.values(), reverse=True)
    margin = sorted_scores[0] - sorted_scores[1]
    confidence = min(1.0, margin * 2)
    return round(confidence, 3)