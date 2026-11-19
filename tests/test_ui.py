from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "ui" / "app.py")


class FakeResponse:
    def __init__(self, data):
        self.data = data
    def raise_for_status(self):
        pass
    def json(self):
        return self.data


def fake_request(method, url, json=None, timeout=None):
    if url.endswith("/ask"):
        return FakeResponse({"answer": "CS-301 has 5 credits [1]",
                             "citations": [{"source": "Updated-AICTE_-_UG_CSE.pdf", "page": 85, "title": "PCC CS-301"}],
                             "retrieved": []})
    if url.endswith("/feedback"):
        fake_request.feedback.append(json)
        return FakeResponse({"saved": True})
    raise AssertionError("unexpected call " + url)


fake_request.feedback = []


def test_card_tab_shows_chain_and_bars():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    at.selectbox[0].select("BSC-301").run()
    html = " ".join(m.value for m in at.markdown)
    assert "BSC-102" in html and "BSC-201" in html          # the chain back to semester 1
    assert "Partial differential equations" in html          # the module legend


def test_every_course_card_renders():
    at = AppTest.from_file(APP, default_timeout=30).run()
    for code in at.selectbox[0].options:
        at.selectbox[0].select(code).run()
        assert not at.exception, code


def test_chat_shows_answer_with_citation_and_saves_feedback(monkeypatch):
    import requests
    monkeypatch.setattr(requests, "request", fake_request)
    fake_request.feedback.clear()
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.chat_input[0].set_value("How many credits is CS-301?").run()
    assert not at.exception
    text = " ".join(m.value for m in at.markdown)
    assert "page 85" in text and "PCC CS-301" in text
    at.button(key="up1").click().run()
    assert fake_request.feedback and fake_request.feedback[0]["rating"] == "up"