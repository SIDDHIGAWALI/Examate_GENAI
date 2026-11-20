import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

RECORDS_PATH = Path(__file__).resolve().parent.parent / "data" / "records.json"
RECORDS = json.loads(RECORDS_PATH.read_text(encoding="utf-8"))


def test_records_file_has_19_courses():
    assert len(RECORDS) == 19


def test_course_codes_are_unique():
    codes = [r["course_code"] for r in RECORDS]
    assert len(codes) == len(set(codes))


def test_every_record_has_title_and_valid_semester():
    for r in RECORDS:
        assert r["course_title"].strip() != ""
        assert r["semester"] in (1, 2, 3)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert "ok" in str(r.json()).lower()


def test_records_endpoint():
    r = client.get("/records")
    assert r.status_code == 200


def test_one_record_found():
    r = client.get("/records/CS-301")
    assert r.status_code == 200
    assert "CS-301" in r.text


def test_unknown_record_is_404():
    r = client.get("/records/NOPE-999")
    assert r.status_code == 404


def test_search_endpoint():
    r = client.get("/search", params={"q": "data structures"})
    assert r.status_code == 200


def test_ask_uses_fake_answer(monkeypatch):
    def fake_answer(question, *args, **kwargs):
        return {"answer": "FAKE ANSWER [1]", "citations": [], "retrieved": []}

    class FakeCollection:
        def count(self):
            return 1

    # CI has no built vector index, so stub the "index is empty" guard as well.
    monkeypatch.setattr("app.vectorstore.get_collection", lambda *a, **k: FakeCollection())
    monkeypatch.setattr("app.rag.answer", fake_answer)
    r = client.post("/ask", json={"question": "How many credits is CS-301?"})
    assert r.status_code == 200
    assert "FAKE ANSWER" in r.text


def test_feedback_rejects_bad_rating():
    r = client.post("/feedback", json={"rating": "maybe"})
    assert r.status_code in (400, 422)