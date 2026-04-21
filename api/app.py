from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import run_pipeline

app = FastAPI()

class AnswersInput(BaseModel):
    answers: dict[str, str]

@app.post("/recommend")
def recommend(data: AnswersInput):
    result = run_pipeline(data.answers)
    return result