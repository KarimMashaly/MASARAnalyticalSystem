
from pipeline import run_pipeline
import json 
import arabic_reshaper
from bidi.algorithm import get_display

def arabic_print(text, end="\n"):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    print(bidi_text, end=end)


def read_questions(file_path=r"E:\\Documents\\Masar\\Analytical System\\MASAR_Analytical_System\\Data\\Questions.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
             return json.load(f)
    
questions = read_questions()


def ask_questions(questions=questions):
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