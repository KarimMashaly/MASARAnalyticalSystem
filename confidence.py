def compute_confidence(scores):

    sorted_scores = sorted(scores.values(), reverse=True)
    top = sorted_scores[0]
    second = sorted_scores[1] if len(sorted_scores) > 1 else 0

    confidence = (top - second) / (top + 1e-6)
    return confidence 
   