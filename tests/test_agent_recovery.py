from app import agent_loop


def test_parse_decision_normal_shape():
    d = agent_loop.parse_decision('{"action": "final", "input": {}, "answer": "hi"}')
    assert d == {"action": "final", "input": {}, "answer": "hi"}


def test_parse_decision_converts_tool_call_shape():
    d = agent_loop.parse_decision('{"name": "ltp_credit_calculator", "arguments": {"semester": 2}}')
    assert d["action"] == "ltp_credit_calculator"
    assert d["input"] == {"semester": 2}


def test_parse_decision_garbage_becomes_final():
    d = agent_loop.parse_decision("just some words")
    assert d["action"] == "final"
    assert d["answer"] == "just some words"


def test_decide_recovers_tool_call_from_provider_400(monkeypatch):
    def fake_llm(system, user):
        raise Exception(
            r'400 {"failed_generation":"{\"name\": \"search_curriculum\", '
            r'\"arguments\": {\"question\":\"credits\"}}"}'
        )

    monkeypatch.setattr(agent_loop, "ask_llm", fake_llm)
    d = agent_loop.decide("credits?", [], [])
    assert d["action"] == "search_curriculum"
    assert d["input"] == {"question": "credits"}


def test_decide_reports_unrecoverable_error(monkeypatch):
    def fake_llm(system, user):
        raise Exception("network down")

    monkeypatch.setattr(agent_loop, "ask_llm", fake_llm)
    d = agent_loop.decide("credits?", [], [])
    assert d["action"] == "final"
    assert "LLM call failed" in d["answer"]