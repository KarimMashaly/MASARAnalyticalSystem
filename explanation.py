def explain(user, track, probs, confidence_info, TRACK_PROFILES):
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
        "Frontend": ["execution", "visual", "ideation", "trial"]
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
        key=lambda t: user[t] * weights.get(t, 0),
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

    if second in track_key_traits:
        second_traits = track_key_traits[second]

        missing = sorted(
            second_traits,
            key=lambda t: user[t]
        )[:2]

        missing_text = [trait_text[t] for t in missing]

        explanation.append(
            f"مقارنةً بـ {second}، التراك ده أقرب ليك لأنك محتاج تطور "
            + " و".join(missing_text) + "."
        )

    # --- development (based on importance not just low value) ---
    weak = ranked[-2:]
    weak_text = [trait_text[t] for t in weak]

    explanation.append(
        f"لو حبيت تطور نفسك أكتر في تراك {second} ، ركز على "
        + " و".join(weak_text) + "."
    )

    # --- probabilities display ---
    sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    probs_text = " | ".join([f"{k}: {round(v*100)}%" for k, v in sorted_probs])

    explanation.append("نسبة التوافق: " + probs_text)

    # --- closing ---
    explanation.append(tone["closing"])

    return explanation