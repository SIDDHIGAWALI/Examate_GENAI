import json
import pytest

from app import agent_loop
from app.graph import build_graph
from langgraph.types import Command

CALC_SEM2 = json.dumps({"action": "ltp_credit_calculator", "input": {"semester": 2}, "answer": ""})
FINAL = json.dumps({"action": "final", "input": {}, "answer": "Semester 2 has 23 credits."})


def scripted_llm(replies):
    # a fake LLM that returns the given replies one by one
    items = list(replies)
    def fake(system, user):
        return items.pop(0)
    return fake


# ---------- hand-written loop ----------

def test_parse_plain_json():
    d = agent_loop.parse_decision(CALC_SEM2)
    assert d["action"] == "ltp_credit_calculator" and d["input"] == {"semester": 2}


def test_parse_json_inside_code_fence():
    d = agent_loop.parse_decision("```json\n" + FINAL + "\n```")
    assert d["action"] == "final"


def test_parse_bad_text_becomes_final_answer():
    d = agent_loop.parse_decision("just some words")
    assert d["action"] == "final" and d["answer"] == "just some words"


def test_unknown_tool_returns_error():
    assert "unknown tool" in agent_loop.run_tool("delete_everything", {})["error"]


def test_tool_with_wrong_arguments_returns_error():
    assert "error" in agent_loop.run_tool("ltp_credit_calculator", {"banana": 1})


def test_loop_calls_calculator_then_answers(monkeypatch):
    monkeypatch.setattr(agent_loop, "ask_llm", scripted_llm([CALC_SEM2, FINAL]))
    out = agent_loop.run_agent("total credits semester 2?")
    assert out["answer"] == "Semester 2 has 23 credits."
    assert [s["tool"] for s in out["steps"]] == ["ltp_credit_calculator"]
    assert out["steps"][0]["result"]["total_listed_credits"] == 23


def test_loop_can_use_search_tool(monkeypatch):
    fake_search = lambda question: {"answer": "CS-301 [1]", "citations": [{"page": 85}]}
    monkeypatch.setitem(agent_loop.TOOLS, "search_curriculum", fake_search)
    ask = json.dumps({"action": "search_curriculum", "input": {"question": "DSA credits"}, "answer": ""})
    monkeypatch.setattr(agent_loop, "ask_llm", scripted_llm([ask, FINAL]))
    out = agent_loop.run_agent("DSA credits?")
    assert out["steps"][0]["result"]["citations"][0]["page"] == 85


def test_loop_stops_after_max_steps(monkeypatch):
    monkeypatch.setattr(agent_loop, "ask_llm", lambda system, user: CALC_SEM2)   # never says final
    out = agent_loop.run_agent("loop forever")
    assert "stopped" in out["answer"]
    assert len(out["steps"]) == agent_loop.MAX_STEPS


def test_loop_survives_llm_failure(monkeypatch):
    def broken(system, user):
        raise RuntimeError("no network")
    monkeypatch.setattr(agent_loop, "ask_llm", broken)
    assert "LLM call failed" in agent_loop.run_agent("hi")["answer"]


# ---------- LangGraph version ----------

@pytest.fixture
def graph():
    return build_graph()      # a fresh graph, so memory is empty for each test


def start(question):
    return {"question": question, "observations": [], "decision": {}, "steps": 0, "approved": False, "answer": ""}


def test_graph_waits_for_approval_before_tool(monkeypatch, graph):
    monkeypatch.setattr(agent_loop, "ask_llm", scripted_llm([CALC_SEM2, FINAL]))
    config = {"configurable": {"thread_id": "a"}}
    result = graph.invoke(start("total credits semester 2?"), config)
    assert result["__interrupt__"][0].value["tool"] == "ltp_credit_calculator"


def test_graph_runs_tool_after_approval(monkeypatch, graph):
    monkeypatch.setattr(agent_loop, "ask_llm", scripted_llm([CALC_SEM2, FINAL]))
    config = {"configurable": {"thread_id": "b"}}
    graph.invoke(start("total credits semester 2?"), config)
    result = graph.invoke(Command(resume=True), config)
    assert result["answer"] == "Semester 2 has 23 credits."
    assert result["observations"][0]["result"]["total_listed_credits"] == 23


def test_graph_does_not_run_tool_when_rejected(monkeypatch, graph):
    monkeypatch.setattr(agent_loop, "ask_llm", scripted_llm([CALC_SEM2, FINAL]))
    config = {"configurable": {"thread_id": "c"}}
    graph.invoke(start("total credits semester 2?"), config)
    result = graph.invoke(Command(resume=False), config)
    assert "did not run" in result["answer"]
    assert result["observations"] == []


def test_graph_asks_approval_only_once_per_question(monkeypatch, graph):
    sem3 = json.dumps({"action": "ltp_credit_calculator", "input": {"semester": 3}, "answer": ""})
    monkeypatch.setattr(agent_loop, "ask_llm", scripted_llm([CALC_SEM2, sem3, FINAL]))
    config = {"configurable": {"thread_id": "d"}}
    graph.invoke(start("compare semester 2 and 3"), config)
    result = graph.invoke(Command(resume=True), config)     # second tool call runs without asking again
    assert "__interrupt__" not in result
    assert len(result["observations"]) == 2


def test_graph_remembers_earlier_turns(monkeypatch, graph):
    seen = []
    def fake(system, user):
        seen.append(user)
        return FINAL
    monkeypatch.setattr(agent_loop, "ask_llm", fake)
    config = {"configurable": {"thread_id": "e"}}
    graph.invoke(start("first question"), config)
    graph.invoke(start("second question"), config)
    assert "User: first question" in seen[1]


def test_graph_threads_do_not_share_memory(monkeypatch, graph):
    seen = []
    def fake(system, user):
        seen.append(user)
        return FINAL
    monkeypatch.setattr(agent_loop, "ask_llm", fake)
    graph.invoke(start("secret question"), {"configurable": {"thread_id": "f1"}})
    graph.invoke(start("other question"), {"configurable": {"thread_id": "f2"}})
    assert "secret question" not in seen[1].split("QUESTION:")[0]