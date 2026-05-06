from pipeline import run_pipeline
import arabic_reshaper
from bidi.algorithm import get_display
import json


def read_qeustions(file_path=r"Data\Questions.json"):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    

def arabic_print(text, end="\n"):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    print(bidi_text, end=end)


def ask_questions(questions= read_qeustions()):
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


answers_shahd = """
B
B 
D
B
A
A
C
A
C
C
B
A
A
A
C
C
A
C
D
B
B
C
A
A
A
D""".replace("\n", "").replace(" ", "")
dict_answers = {}
for id ,  v in enumerate(answers_shahd, 1):
     dict_answers[str(id)] = v

print(dict_answers)



if __name__ == "__main__":
    answers =  dict_answers  #      ask_questions()         #{"1":"A","2":"A","3":"C","4":"A","5":"A","6":"B","7":"C","8":"A","9":"C","10":"A","11":"A","12":"B","13":"A","14":"C","15":"A","16":"A","17":"B","18":"C","19":"C","20":"A","21":"B","22":"B","23":"C","24":"A","25":"C","26":"C"}
 #
    result = run_pipeline(answers)

    print("\n=== RESULT ===")
    arabic_print("Track: " + result["track"])
    arabic_print("Confidence Score: " + str(result["confidence"]["score"]))
    arabic_print("Confidence Level: " + result["confidence"]["label"])
    arabic_print("Scores: " + str(result["scores"]))
    arabic_print("Traits: " + str(result["traits"]))
    arabic_print("\nExplanation:")
    for line in result["explanation"]:
        arabic_print("- " + line)

