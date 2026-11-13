import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.smart_search import smart_search
from app.chat import chat

app = FastAPI(title="CurriculumBuddy")

with open("data/records.json", encoding="utf-8") as f:
    RECORDS = json.load(f)

QUESTIONS = []


class Question(BaseModel):
    name: str
    question: str


class ChatRequest(BaseModel):
    question: str
    version: str = "v2"


@app.get("/health")
def health():
    return {"status": "ok", "records": len(RECORDS)}


@app.get("/records")
def list_records(limit: int = 10):
    return RECORDS[:limit]


@app.get("/records/{course_code}")
def get_record(course_code: str):
    for r in RECORDS:
        if r["course_code"] == course_code:
            return r
    raise HTTPException(status_code=404, detail="Course not found")


@app.get("/search")
def search(q: str):
    return smart_search(RECORDS, q)


@app.post("/questions")
def ask(question: Question):
    matches = smart_search(RECORDS, question.question, top_k=3)
    QUESTIONS.append({"name": question.name, "question": question.question})
    return {"received": question.question, "related_courses": matches}


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    return chat(RECORDS, request.question, request.version)