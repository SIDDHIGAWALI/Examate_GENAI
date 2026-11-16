import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.vectorstore import get_collection, query as vs_query
from app.llm import ask_llm

router = APIRouter()

RAG_SYSTEM = """You are CurriculumBuddy. Answer ONLY from the CONTEXT CHUNKS below.
If the chunks do not contain the answer, say exactly: "I don't know."
Never invent facts. Keep it short.
Reply as JSON: {"answer": "...", "sources": [{"source": "...", "page": 1}]}"""


class AskRequest(BaseModel):
    question: str
    k: int = 5


@router.post("/ask")
def ask(req: AskRequest):
    col = get_collection()
    if col.count() == 0:
        raise HTTPException(503, "Index empty. Run: python -m app.vectorstore")

    hits = vs_query(req.question, k=req.k)

    context = ""
    for i, h in enumerate(hits, 1):
        context += f"[{i}] {h['source']} p{h['page']}\n{h['text']}\n\n"

    prompt = f"QUESTION: {req.question}\n\nCONTEXT CHUNKS:\n{context}"

    try:
        raw = ask_llm(RAG_SYSTEM, prompt)
    except Exception as e:
        raise HTTPException(502, f"LLM failed: {e}")

    # parse JSON reply
    clean = raw.strip().strip("`")
    if clean.lower().startswith("json"):
        clean = clean[4:]
    try:
        data = json.loads(clean)
    except Exception:
        data = {"answer": clean, "sources": []}

    return {
        "question": req.question,
        "answer": data.get("answer", clean),
        "sources": data.get("sources", []),
    }