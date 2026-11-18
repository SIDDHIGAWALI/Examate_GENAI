from app.tools import ltp_credit_calculator


def test_one_course_matches_table():
    r = ltp_credit_calculator(l=3, t=0, p=4, listed_credits=5)
    assert r["credits"] == 5
    assert r["contact_hours_per_week"] == 7
    assert r["matches_table"] is True


def test_practical_hours_count_half():
    assert ltp_credit_calculator(l=0, t=0, p=2)["credits"] == 1


def test_division_only_applies_to_practical():
    # (3 + 0 + 2) / 2 would be 2.5, the right answer is 3 + 0 + 2/2 = 4
    assert ltp_credit_calculator(l=3, t=0, p=2)["credits"] == 4


def test_mismatch_is_flagged():
    r = ltp_credit_calculator(l=2, t=0, p=4, listed_credits=0)   # audit course
    assert r["matches_table"] is False


def test_negative_hours_rejected():
    assert "negative" in ltp_credit_calculator(l=-1, t=0, p=2)["error"]


def test_text_instead_of_number_rejected():
    assert "number" in ltp_credit_calculator(l="three", t=0, p=2)["error"]


def test_too_many_hours_rejected():
    assert "too large" in ltp_credit_calculator(l=3, t=0, p=100)["error"]


def test_missing_values_rejected():
    assert "error" in ltp_credit_calculator(l=3)


def test_semester_1_totals_and_audit_mismatch():
    r = ltp_credit_calculator(semester=1)
    assert r["total_listed_credits"] == 18
    assert r["total_calculated_credits"] == 22
    assert [m["course_code"] for m in r["mismatches"]] == ["AU-101"]


def test_semester_2_totals_and_audit_mismatch():
    r = ltp_credit_calculator(semester=2)
    assert r["total_listed_credits"] == 23
    assert [m["course_code"] for m in r["mismatches"]] == ["AU-102"]


def test_semester_3_has_no_mismatch():
    r = ltp_credit_calculator(semester=3)
    assert r["total_listed_credits"] == 23
    assert r["total_calculated_credits"] == 23
    assert r["mismatches"] == []


def test_semester_without_records():
    assert "no courses" in ltp_credit_calculator(semester=4)["error"]


def test_semester_out_of_range():
    assert "between 1 and 8" in ltp_credit_calculator(semester=9)["error"]