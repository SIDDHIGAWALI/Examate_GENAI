import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.smart_search import smart_search
from app.chat import chat
from app import vectorstore, rag
from app.graph import graph
from langgraph.types import Command

app = FastAPI(title="CurriculumBuddy")

with open("data/records.json", encoding="utf-8") as f:
    RECORDS = json.load(f)

QUESTIONS = []


class Question(BaseModel):
    name: str
    question: str


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


class AskRequest(BaseModel):
    question: str
    k: int = 3


class AgentRequest(BaseModel):
    message: str = ""
    thread_id: str = "default"
    approve: bool | None = None


class ChatRequest(BaseModel):
    question: str
    version: str = "v2"


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    return chat(RECORDS, request.question, request.version)


@app.get("/search/semantic")
def search_semantic(q: str, k: int = 5):
    if vectorstore.get_collection().count() == 0:
        raise HTTPException(status_code=503, detail="Index is empty. Run: python -m app.vectorstore")
    return vectorstore.query(q, k)


@app.post("/ask")
def ask_endpoint(request: AskRequest):
    if vectorstore.get_collection().count() == 0:
        raise HTTPException(status_code=503, detail="Index is empty. Run: python -m app.vectorstore")
    return rag.answer(request.question, request.k)


@app.post("/agent")
def agent_endpoint(request: AgentRequest):
    config = {"configurable": {"thread_id": request.thread_id}}

    if request.approve is not None:
        result = graph.invoke(Command(resume=request.approve), config)      # answer the approval question
    else:
        if request.message == "":
            raise HTTPException(status_code=400, detail="Send a message, or approve true/false")
        result = graph.invoke({
            "question": request.message, "observations": [], "decision": {},
            "steps": 0, "approved": False, "answer": "",
        }, config)

    if "__interrupt__" in result:
        asked = result["__interrupt__"][0].value
        return {"status": "waiting_for_approval", "thread_id": request.thread_id,
                "tool": asked["tool"], "input": asked["input"],
                "how_to_continue": "POST /agent again with the same thread_id and approve true or false"}
    return {"status": "done", "thread_id": request.thread_id,
            "answer": result["answer"], "tools_used": result["observations"]}