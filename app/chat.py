import json
from app.llm import ask_llm
from app.smart_search import smart_search


def read_prompt(name):
    with open("prompts/" + name, encoding="utf-8") as f:
        return f.read()


def pick_task(question):
    q = question.lower()
    if "plan" in q or "schedule" in q or "week" in q:
        return "task_plan.txt"
    return "task_lookup.txt"


def parse_reply(text):
    # the model should return JSON; remove ``` fences if it added them
    text = text.strip().strip("`")
    if text.lower().startswith("json"):
        text = text[4:]
    try:
        data = json.loads(text)
        return {
            "answer": str(data.get("answer", "")),
            "confidence": str(data.get("confidence", "low")),
            "follow_up": str(data.get("follow_up", "")),
        }
    except Exception:
        return {"answer": text, "confidence": "low", "follow_up": ""}


def chat(records, question, version="v2"):
    system_file = "system.txt" if version == "v2" else "system_v1.txt"
    system = read_prompt(system_file) + "\n" + read_prompt(pick_task(question))

    matches = smart_search(records, question, top_k=3)
    context = json.dumps([m["record"] for m in matches], indent=1)
    user = "QUESTION: " + question + "\n\nCOURSE RECORDS:\n" + context

    try:
        reply = ask_llm(system, user)
    except Exception as e:
        return {"answer": "LLM call failed: " + str(e), "confidence": "low", "follow_up": ""}
    return parse_reply(reply)