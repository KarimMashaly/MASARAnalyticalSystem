def compute_confidence(scores):
    sorted_scores = sorted(scores.values(), reverse=True)

    gap = sorted_scores[0] - sorted_scores[1]

    return round(min(1.0, gap * 1.5), 3)