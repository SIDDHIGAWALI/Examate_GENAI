import json

from fastapi.testclient import TestClient

from app import main
from ui import cards as cardlib

RECORDS = cardlib.load_records()
CARDS = cardlib.load_cards()
BY_CODE = {r["course_code"]: r for r in RECORDS}


def test_every_record_has_a_card_and_no_extra_cards():
    assert sorted(BY_CODE) == sorted(CARDS)


def test_prerequisites_point_to_earlier_semesters():
    for code, card in CARDS.items():
        for p in card["prerequisites"]:
            assert p["code"] in BY_CODE
            assert BY_CODE[p["code"]]["semester"] < BY_CODE[code]["semester"]
            assert p["basis"] != ""


def test_module_durations_are_positive_numbers_with_a_unit():
    for card in CARDS.values():
        for m in card["modules"]:
            if m["hours"] is not None:
                assert m["hours"] > 0 and m["unit"] in ("hours", "lectures", "weeks")


def test_chain_for_mathematics_3_goes_back_to_semester_1():
    paths = cardlib.prerequisite_paths("BSC-301", CARDS, BY_CODE)
    assert paths == [["BSC-102", "BSC-201", "BSC-301"]]


def test_first_semester_course_has_no_chain():
    assert cardlib.prerequisite_paths("BSC-102", CARDS, BY_CODE) == []


def test_chain_ignores_same_semester_courses():
    cards = {"BSC-102": {"prerequisites": [{"code": "ESC-101", "basis": "test"}]}}
    assert cardlib.prerequisite_paths("BSC-102", cards, BY_CODE) == []


def test_bars_are_proportional_when_all_durations_are_known():
    strip = cardlib.module_strip(CARDS["BSC-102"]["modules"])      # 6, 6, 10, 8, 10 hours
    assert strip["mode"] == "proportional" and strip["total"] == 40
    assert round(sum(s["percent"] for s in strip["segments"])) == 100
    assert strip["segments"][2]["percent"] == 25


def test_bars_use_weeks_for_data_structures():
    strip = cardlib.module_strip(CARDS["CS-301"]["modules"])
    assert strip["mode"] == "proportional" and strip["unit"] == "weeks" and strip["total"] == 15.5


def test_bars_are_equal_when_durations_are_missing():
    strip = cardlib.module_strip(CARDS["ESC-101"]["modules"])
    assert strip["mode"] == "equal"
    assert all(s["label"] == "duration not stated" for s in strip["segments"])


def test_partial_durations_do_not_make_fake_bars():
    strip = cardlib.module_strip(CARDS["BSC-202"]["modules"])      # only module 4 has a duration
    assert strip["mode"] == "equal"
    assert [s["label"] for s in strip["segments"]].count("6 lectures") == 1


def test_course_without_modules_draws_nothing():
    strip = cardlib.module_strip([])
    assert strip["mode"] == "none" and cardlib.strip_html(strip) == ""


def test_html_escapes_text():
    strip = cardlib.module_strip([{"name": "<script>alert(1)</script>", "hours": 2, "unit": "hours"}])
    assert "<script>" not in cardlib.strip_html(strip) + cardlib.legend_html(strip)


def test_feedback_is_saved(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "FEEDBACK_PATH", str(tmp_path / "feedback.jsonl"))
    client = TestClient(main.app)
    r = client.post("/feedback", json={"question": "q", "answer": "a", "rating": "up", "mode": "ask"})
    assert r.status_code == 200
    saved = json.loads((tmp_path / "feedback.jsonl").read_text(encoding="utf-8").strip())
    assert saved["rating"] == "up" and saved["question"] == "q"


def test_feedback_rejects_other_ratings(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "FEEDBACK_PATH", str(tmp_path / "feedback.jsonl"))
    client = TestClient(main.app)
    assert client.post("/feedback", json={"question": "q", "answer": "a", "rating": "maybe"}).status_code == 422