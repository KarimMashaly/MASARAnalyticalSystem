
from pipeline import run_pipeline
import arabic_reshaper
from bidi.algorithm import get_display

QUESTIONS =  [
  {
    "id": "1",
    "text": "لما تدخل على موضوع جديد ومش واضح...",
    "options": {
      "A": "أستنى لحد ما الصورة تبقى واضحة",
      "B": "أحاول أفهمه تدريجي حتى لو مش كامل",
      "C": "أحط افتراضات وأبدأ أشتغل",
      "D": "أسيبه مؤقتًا وأرجع له بعدين"
    }
  },
  {
    "id": "2",
    "text": "فكرت تعمل حاجة جديدة في وقت فراغك...",
    "options": {
      "A": "أبدأ أنفذ فورًا",
      "B": "أفكر في أفكار مختلفة",
      "C": "أشوف أفكار ناس تانية وأبني عليها",
      "D": "أرتب الفكرة وأحدد خطوات التنفيذ"
    }
  },
  {
    "id": "3",
    "text": "كل مرة بتحل المشكلة وتطلع غلط، أول حاجة تعملها...",
    "options": {
      "A": "أحلل الخطأ في نفس الطريقة",
      "B": "أغير الطريقة بالكامل",
      "C": "أسيبها مؤقتًا",
      "D": "أطلب مساعدة"
    }
  },
  {
    "id": "4",
    "text": "لما بتذاكر موضوع جديد...",
    "options": {
      "A": "أمشي خطوة خطوة بالترتيب",
      "B": "أتنقل بين الأجزاء حسب الحاجة",
      "C": "أركز على جزء واحد لحد ما أفهمه كويس",
      "D": "أجرب بشكل عشوائي"
    }
  },
  {
    "id": "5",
    "text": "قدامك مشكلة كبيرة...",
    "options": {
      "A": "أفهم الصورة العامة الأول",
      "B": "أقسمها لأجزاء صغيرة",
      "C": "أجرب حلول مباشرة",
      "D": "أشوف مثال مشابه"
    }
  },
  {
    "id": "6",
    "text": "عندك task مش محدد قوي...",
    "options": {
      "A": "أستنى تفاصيل أكتر",
      "B": "أبدأ بحاجة بسيطة وأعدل",
      "C": "أأجل لحد ما يبقى أوضح",
      "D": "أشتغل على فهمي الحالي وأكمل"
    }
  },
  {
    "id": "7",
    "text": "مش متأكد إن الحل صح...",
    "options": {
      "A": "أكمل وأعدل لو احتاج",
      "B": "أوقف لحد ما أتأكد",
      "C": "أراجع تحليلي",
      "D": "أجرب طريقة تانية"
    }
  },
  {
    "id": "8",
    "text": "لما تيجي تفكر في مشروع جديد...",
    "options": {
      "A": "أتخيل شكله وتجربة استخدامه",
      "B": "أفكر في الفكرة وإزاي تكون مختلفة",
      "C": "أركز على أسرع طريقة لتنفيذه",
      "D": "أفكر إزاي أخليه شغال بكفاءة"
    }
  },
  {
    "id": "9",
    "text": "لما تشتغل على حاجة ليها حل معروف...",
    "options": {
      "A": "أعملها زي ما هي عشان أوفر وقت",
      "B": "أعدل عليها لو في فايدة",
      "C": "ألتزم بالحل لأنه مضمون",
      "D": "أجرب أفكار مختلفة حتى لو فيها مخاطرة"
    }
  },
  {
    "id": "10",
    "text": "لما حد يديك فكرة عامة...",
    "options": {
      "A": "أطورها وأضيف أفكار جديدة",
      "B": "أجربها بشكل عملي",
      "C": "أبحث عنها وأفهمها كويس",
      "D": "أسأل عن تفاصيل أكتر"
    }
  }
]


def arabic_print(text, end="\n"):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    print(bidi_text, end=end)



def ask_questions(questions=QUESTIONS):
    answers = {}

    for q in questions:
        arabic_print("\n" + q["text"])
        for k, v in q["options"].items():
            arabic_print(f"{k}) {v}")

        while True:
            arabic_print("اختار: ", end="")
            ans = input(": ").strip().upper()
            if ans in q["options"]:
                answers[q["id"]] = ans
                break
            else:
                arabic_print("اختيار غير صحيح")

    return answers


if __name__ == "__main__":
    answers = ask_questions()
    result = run_pipeline(answers)

    print("\n=== RESULT ===")
    arabic_print("Track: " + result["track"])
    arabic_print("Confidence: " + str(result["confidence"]))
    arabic_print("Traits: " + str(result["traits"]))
    arabic_print("Explanation:")
    for line in result["explanation"]:
        arabic_print("- " + line)