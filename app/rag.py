import re

from app import vectorstore
from app.llm import ask_llm


def read_prompt(name):
    with open("prompts/" + name, encoding="utf-8") as f:
        return f.read()


def is_unknown(answer):
    text = answer.lower().replace("\u2019", "'")
    return "i don't know" in text


def answer(question, k=3, collection=vectorstore.COLLECTION):
    # 1. find the best chunks
    hits = vectorstore.query(question, k=k, name=collection, max_chars=None)

    # 2. give them to the LLM, numbered, so it can cite them
    parts = []
    for number, h in enumerate(hits, start=1):
        parts.append(f"[{number}] ({h['source']}, page {h['page']}, {h['title']})\n{h['text']}")
    user = "QUESTION: " + question + "\n\nCHUNKS:\n\n" + "\n\n".join(parts)

    retrieved = [{"source": h["source"], "page": h["page"], "title": h["title"], "score": h["score"]} for h in hits]

    try:
        reply = ask_llm(read_prompt("rag_system.txt"), user).strip()
    except Exception as e:
        return {"answer": "LLM call failed: " + str(e), "citations": [], "retrieved": retrieved}

    # 3. turn the [1] [2] markers into citations
    citations = []
    if not is_unknown(reply):
        numbers = sorted(set(int(n) for n in re.findall(r"\[(\d+)\]", reply)))
        for n in numbers:
            if 1 <= n <= len(hits):
                h = hits[n - 1]
                citations.append({"source": h["source"], "page": h["page"], "title": h["title"]})
    return {"answer": reply, "citations": citations, "retrieved": retrieved}