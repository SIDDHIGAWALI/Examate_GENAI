import operator
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from app.agent_loop import decide, run_tool, MAX_STEPS


class AgentState(TypedDict):
    question: str
    history: Annotated[list, operator.add]   # memory: grows with every turn, kept per thread_id
    observations: list                       # tool results for the current question
    decision: dict                           # what the model wants to do next
    steps: int
    approved: bool
    answer: str


def agent_node(state):
    decision = decide(state["question"], state["history"], state["observations"])
    return {"decision": decision, "steps": state["steps"] + 1}


def after_agent(state):
    if state["decision"]["action"] == "final":
        return "finish"
    if state["steps"] > MAX_STEPS:
        return "finish"
    if state["approved"]:
        return "tools"          # already approved for this question
    return "approval"


def approval_node(state):
    # the graph stops here and waits until the user answers (approve true / false)
    ok = interrupt({"tool": state["decision"]["action"], "input": state["decision"]["input"]})
    return {"approved": bool(ok)}


def after_approval(state):
    return "tools" if state["approved"] else "rejected"


def tools_node(state):
    d = state["decision"]
    result = run_tool(d["action"], d["input"])
    return {"observations": state["observations"] + [{"tool": d["action"], "input": d["input"], "result": result}]}


def rejected_node(state):
    answer = "Okay, I did not run the tool, so I cannot answer that."
    return {"answer": answer, "history": ["User: " + state["question"], "Agent: " + answer]}


def finish_node(state):
    answer = state["decision"]["answer"] or "I stopped without a final answer."
    return {"answer": answer, "history": ["User: " + state["question"], "Agent: " + answer]}


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("agent", agent_node)
    g.add_node("approval", approval_node)
    g.add_node("tools", tools_node)
    g.add_node("rejected", rejected_node)
    g.add_node("finish", finish_node)

    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", after_agent, {"finish": "finish", "tools": "tools", "approval": "approval"})
    g.add_conditional_edges("approval", after_approval, {"tools": "tools", "rejected": "rejected"})
    g.add_edge("tools", "agent")
    g.add_edge("finish", END)
    g.add_edge("rejected", END)
    return g.compile(checkpointer=MemorySaver())   # MemorySaver keeps the memory per thread_id


graph = build_graph()