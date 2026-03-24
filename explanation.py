def explain(user, track):
    trait_text = {
        "analytical": "تفكير تحليلي قوي",
        "structure": "أسلوب منظم",
        "execution": "قدرة على التنفيذ",
        "ambiguity": "القدرة على التعامل مع الغموض",
        "trial": "حب التجربة",
        "frustration": "الاستمرار رغم الصعوبة"
    }

    sorted_traits = sorted(user.items(), key=lambda x: x[1], reverse=True)

    strong = sorted_traits[:2]
    weak = sorted_traits[-2:]

    explanation = []

    explanation.append(
        "أنت تتميز بـ " + " و ".join([trait_text[t[0]] for t in strong])
    )

    explanation.append(
        "وقد تحتاج لتطوير " + " و ".join([trait_text[t[0]] for t in weak])
    )

    if track == "AI":
        explanation.append("تم اختيار AI لأنك قوي في التحليل وتتحمل الغموض")

    elif track == "Backend":
        explanation.append("تم اختيار Backend لأنك منظم وتميل للتنفيذ المستمر")

    elif track == "Frontend":
        explanation.append("تم اختيار Frontend لأنك تميل للتجربة والتنفيذ")

    return explanation