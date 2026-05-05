def normalize_for_display(scores):
    # 1) remove negatives
    clipped = {k: max(0, v) for k, v in scores.items()}

    # 2) handle edge case (all zero)
    total = sum(clipped.values())
    if total == 0:
        return {k: 0 for k in scores}

    # 3) normalize
    return {k: v / total for k, v in clipped.items()}


def explain(user_traits, track, scores, confidence_info, TRACK_PROFILES):
    trait_text = {
        "analytical":  "تفكير تحليلي قوي",
        "structure":   "أسلوب منظم ومنهجي",
        "execution":   "قدرة عالية على التنفيذ",
        "ambiguity":   "ارتياح مع الغموض وعدم اليقين",
        "trial":       "روح تجريبية واستعداد للمحاولة",
        "frustration": "مثابرة واستمرار رغم الصعوبة",
        "ideation":    "قدرة على توليد أفكار إبداعية",
        "precision":   "اهتمام بالتفاصيل والدقة",
        "visual":      "تفكير بصري وحساسية لتجربة المستخدم",
        "pattern":     "قدرة على اكتشاف الأنماط"
    }

    track_key_traits = {
        "AI":       ["analytical", "pattern", "ambiguity", "frustration"],
        "Backend":  ["analytical", "structure", "precision", "execution"],
        "Frontend": ["execution", "visual", "ideation", "trial"],
        "Mobile":   ["execution", "visual", "trial", "structure"],
        "Testing":  ["precision", "analytical", "pattern", "structure"]
    }

    tone_templates = {
        "high": {
            "intro": "واضح جدًا إن {track} هو الأنسب ليك.",
            "reason": "أسلوبك متوافق بشكل قوي مع متطلبات التراك ده.",
            "closing": "الاختيار ده بيعكس شخصيتك بشكل دقيق."
        },
        "medium": {
            "intro": "أقرب اختيار ليك هو {track}.",
            "reason": "في توافق واضح مع التراك ده، مع وجود بعض التقاطعات.",
            "closing": "ممكن تلاقي نفسك بين أكتر من تراك، لكن ده الأقرب حاليًا."
        },
        "low": {
            "intro": "في أكتر من تراك قريبين من أسلوبك، لكن {track} هو الأقرب.",
            "reason": "نتيجتك بتوضح إنك عندك مزيج من المهارات أو لسه في مرحلة استكشاف.",
            "closing": "ممكن تحتاج تجربة أكتر عشان تحدد الاتجاه الأنسب ليك."
        }
    }

    explanation = []

    # --- tone ---
    label = confidence_info["label"]
    tone = tone_templates[label]

    # --- get weights ---
    weights = {
        t: w for t, (_, _, w) in TRACK_PROFILES[track]["traits"].items()
    }

    # --- sort relevant traits by importance ---
    relevant_traits = track_key_traits[track]

    ranked = sorted(
        relevant_traits,
        key=lambda t: user_traits[t] * weights.get(t, 0),
        reverse=True
    )

    # --- strengths ---
    strong = [trait_text[t] for t in ranked[:2]]
    explanation.append("أقوى حاجة بتميزك هي " + " و".join(strong) + ".")

    # --- tone intro ---
    explanation.append(tone["intro"].format(track=track))
    explanation.append(tone["reason"])

    # --- WHY NOT second track ---
    second = confidence_info["second_track"]

    weights_second = {
t: w for t, (_, _, w) in TRACK_PROFILES[second]["traits"].items()
}

    missing = sorted(
        weights_second,
        key=lambda t: (1 - user_traits[t]) * weights_second.get(t, 0),
        reverse=True
    )

    # فلترة: ناخد بس المهم فعلًا
    missing = [
        t for t in missing
        if weights_second.get(t, 0) > 0.1 and user_traits[t] < 0.6
][:2]

    missing_text = [trait_text[t] for t in missing]

    explanation.append(
            f"مقارنةً بـ {second}، التراك ده أقرب ليك لأنك محتاج تطور "
            + " و".join(missing_text) + "."
        )

   

    # --score display ---
    percent = normalize_for_display(scores)
    sorted_percent = sorted(percent.items(), key=lambda x: x[1], reverse=True)

    score_text = " | ".join([
        f"{k}: {round(v*100)}%" for k, v in sorted_percent
    ])

    explanation.append("نسبة التوافق (حسب الأداء): " + score_text)

        # --- closing ---
    explanation.append(tone["closing"])

    return explanation
