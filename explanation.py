def explain(traits, track):
    mapping = {
        "analytical": "تحليل المشاكل بعمق",
        "structure": "الالتزام بخطوات واضحة",
        "execution": "البدء والتنفيذ بسرعة",
        "ambiguity": "التعامل مع الغموض",
        "trial": "التجربة والمحاولة",
        "frustration": "الاستمرار رغم الصعوبة"
    }
    
    traits = {k: v for k, v in traits.items() if k in mapping}
    
    strong = sorted(traits.items(), key=lambda x: x[1], reverse=True)[:2]
    weak = sorted(traits.items(), key=lambda x: x[1])[:2]

    explanation = []
    explanation.append("أنت تميل إلى " + " و ".join([mapping[t[0]] for t in strong]))
    explanation.append("وقد تحتاج لتطوير " + " و ".join([mapping[t[0]] for t in weak]))

    if track == "AI":
        explanation.append("مناسب لك مجال الذكاء الاصطناعي لأنك تحب التحليل وتتحمل الغموض")
    elif track == "Backend":
        explanation.append("مناسب لك الباك إند لأنك منظم وتحب بناء أنظمة واضحة")
    else:
        explanation.append("مناسب لك الفرونت إند لأنك تحب التجربة والتنفيذ")

    return explanation