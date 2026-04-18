def explain(user, track, scores):
    trait_text = {
        "analytical": "تفكير تحليلي قوي",
        "structure": "أسلوب منظم",
        "execution": "قدرة على التنفيذ",
        "ambiguity": "القدرة على التعامل مع الغموض",
        "trial": "حب التجربة",
        "frustration": "الاستمرار رغم الصعوبة",
        "ideation": "قدرة على توليد أفكار"
    }

    # ------------------------
    # 1) Top traits (القوة الحقيقية)
    # ------------------------
    sorted_traits = sorted(user.items(), key=lambda x: x[1], reverse=True)
    strong = sorted_traits[:3]

    strong_text = [trait_text[t[0]] for t in strong]

    explanation = []

    explanation.append(
        "من أسلوبك، واضح أنك تتميز بـ " + " و ".join(strong_text)
    )

    # ------------------------
    # 2) Track-specific reasoning
    # ------------------------
    track_logic = {
        "AI": ["analytical", "ambiguity", "trial"],
        "Backend": ["analytical", "structure", "execution"],
        "Frontend": ["execution", "trial", "ideation"]
    }

    relevant_traits = track_logic[track]

    matched = []
    for t in relevant_traits:
        if user[t] > 0.6:
            matched.append(trait_text[t])

    if matched:
        explanation.append(
            f"وده مناسب لتراك {track} لأنك تمتلك " + " و ".join(matched)
        )

    # ------------------------
    # 3) Weak traits (لكن بلطف)
    # ------------------------
    weak = sorted_traits[-2:]
    weak_text = [trait_text[t[0]] for t in weak]

    explanation.append(
        "ممكن كمان تطور " + " و ".join(weak_text) + " لنتائج أفضل"
    )

    # ------------------------
    # 4) Confidence explanation
    # ------------------------
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_score = sorted_scores[0][1]
    second_score = sorted_scores[1][1]

    gap = top_score - second_score

    if gap < 0.05:
        explanation.append("الاختيار كان قريب من أكتر من تراك، فممكن تكون مناسب لأكتر من مجال")
    elif gap < 0.15:
        explanation.append("التراك ده مناسب لك، لكن في اختيارات تانية قريبة منه")
    else:
        explanation.append("النتيجة واضحة جدًا وبتعبر بشكل قوي عن أسلوبك")

    return explanation