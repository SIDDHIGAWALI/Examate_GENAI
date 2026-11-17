import json
import re

from app import rag
from app.llm import ask_llm
from app.tools import ltp_credit_calculator

MAX_STEPS = 5


def read_prompt(name):
    with open("prompts/" + name, encoding="utf-8") as f:
        return f.read()


def search_curriculum(question):
    return rag.answer(question, k=3)


# the tools the agent may call: name -> function
TOOLS = {
    "search_curriculum": search_curriculum,
    "ltp_credit_calculator": ltp_credit_calculator,
}


def run_tool(name, tool_input):
    if name not in TOOLS:
        return {"error": "unknown tool: " + str(name)}
    try:
        return TOOLS[name](**tool_input)
    except Exception as e:
        return {"error": str(e)}


def parse_decision(text):
    # the model should reply with one JSON object; remove ``` fences if present
    cleaned = text.strip().strip("`")
    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:]
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    try:
        data = json.loads(match.group(0))
        return {
            "action": str(data.get("action", "final")),
            "input": data.get("input") or {},
            "answer": str(data.get("answer", "")),
        }
    except Exception:
        return {"action": "final", "input": {}, "answer": text.strip()}


def build_prompt(question, history, observations):
    text = ""
    if history:
        text = text + "EARLIER IN THIS CONVERSATION:\n" + "\n".join(history) + "\n\n"
    text = text + "QUESTION: " + question + "\n\n"
    if observations:
        text = text + "OBSERVATIONS SO FAR:\n"
        for o in observations:
            text = text + "- " + o["tool"] + " " + json.dumps(o["input"]) + " -> " + json.dumps(o["result"]) + "\n"
    else:
        text = text + "OBSERVATIONS SO FAR: none\n"
    return text


def decide(question, history, observations):
    try:
        reply = ask_llm(read_prompt("agent_system.txt"), build_prompt(question, history, observations))
    except Exception as e:
        return {"action": "final", "input": {}, "answer": "LLM call failed: " + str(e)}
    return parse_decision(reply)


def run_agent(question, history=None):
    history = history or []
    observations = []
    for step in range(MAX_STEPS):
        decision = decide(question, history, observations)
        if decision["action"] == "final":
            return {"answer": decision["answer"], "steps": observations}
        result = run_tool(decision["action"], decision["input"])
        observations.append({"tool": decision["action"], "input": decision["input"], "result": result})
    return {"answer": "I stopped after " + str(MAX_STEPS) + " steps without a final answer.", "steps": observations}


if __name__ == "__main__":
    while True:
        q = input("\nAsk the agent (empty to quit): ")
        if q == "":
            break
        out = run_agent(q)
        for s in out["steps"]:
            print("  [tool]", s["tool"], s["input"])
        print("Answer:", out["answer"])