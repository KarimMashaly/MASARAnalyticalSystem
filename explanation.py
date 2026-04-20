def explain(user, track, scores, confidence_info):
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
        "pattern":     "قدرة على اكتشاف الأنماط والعلاقات الخفية"
    }

    track_key_traits = {
        "AI":       ["analytical", "pattern", "ambiguity", "frustration"],
        "Backend":  ["analytical", "structure", "precision", "execution"],
        "Frontend": ["execution", "visual", "ideation", "trial"]
    }

    track_description = {
        "AI": "تراك الـ AI مناسب للناس اللي بتحب تفهم ليه الأشياء بتحصل، مش بس إزاي. محتاج تفكير تحليلي عميق، ارتياح مع بيانات ناقصة، وفضول مستمر.",
        "Backend": "تراك الـ Backend مناسب للناس اللي بتحب تبني أنظمة محكمة وقابلة للاعتماد. محتاج دقة، تنظيم، وتفكير منهجي في كيفية بناء الأشياء صح.",
        "Frontend": "تراك الـ Frontend مناسب للناس اللي بتحب تربط بين الفكرة والتجربة الإنسانية. محتاج تنفيذ سريع، تفكير بصري، وقدرة على التكيف مع التغيير."
    }

    explanation = []

    # 1) Top strengths
    sorted_traits = sorted(user.items(), key=lambda x: x[1], reverse=True)
    strong = [t for t, v in sorted_traits[:3]]
    strong_text = [trait_text[t] for t in strong]
    explanation.append("من أسلوبك في التفكير، واضح إنك بتتميز بـ " + " و".join(strong_text) + ".")

    # 2) Track match reasoning
    relevant = track_key_traits[track]
    matched = [trait_text[t] for t in relevant if user[t] >= 0.58]

    if matched:
        explanation.append(
            f"الـ {track} ده مناسب ليك لأنك بتمتلك " + " و".join(matched) + "."
        )
    else:
        explanation.append(
            f"الـ {track} ده أقرب track لأسلوبك العام، وإن كان في مجال تطوير كمان."
        )

    # 3) Track description
    explanation.append(track_description[track])

    # 4) Development areas
    weak = [t for t, v in sorted_traits[-3:] if t in track_key_traits[track]]
    if weak:
        weak_text = [trait_text[t] for t in weak]
        explanation.append("للنمو في الـ track ده، هيفيدك تطور " + " و".join(weak_text) + ".")

    # 5) Confidence-aware closing
    conf_label = confidence_info["label"]
    second     = confidence_info["second_track"]

    if conf_label == "low":
        explanation.append(
            f"النتيجة دي قريبة جدًا من تراك الـ {second} كمان، "
            "ده ممكن يعني إنك بتتميز بمزيج من المهارتين أو لسه بتكتشف."
        )
    elif conf_label == "medium":
        explanation.append(
            f"النتيجة بتميل واضح لـ {track}، مع وجود تقاطع مع الـ {second}."
        )
    else:
        explanation.append(
            f"النتيجة واضحة وقوية، وده بيعكس أسلوبك بشكل دقيق."
        )

    return explanation
