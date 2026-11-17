import json

RECORDS_PATH = "data/records.json"


def calculate_course(l, t, p, listed_credits=None):
    # AICTE mapping: 1 lecture hour = 1 credit, 1 tutorial hour = 1 credit, 2 practical hours = 1 credit
    credits = l + t + (p / 2)
    contact_hours = l + t + p
    result = {"l": l, "t": t, "p": p, "credits": credits, "contact_hours_per_week": contact_hours}
    if listed_credits is not None:
        result["listed_credits"] = listed_credits
        result["matches_table"] = (credits == listed_credits)
    return result


def calculate_semester(semester):
    with open(RECORDS_PATH, encoding="utf-8") as f:
        records = json.load(f)

    courses = []
    mismatches = []
    total_calculated = 0
    total_listed = 0
    total_hours = 0
    for r in records:
        if r["semester"] != semester:
            continue
        ltp = r["l_t_p_credits"]
        row = calculate_course(ltp["L"], ltp["T"], ltp["P"], ltp["credits"])
        row["course_code"] = r["course_code"]
        courses.append(row)
        total_calculated = total_calculated + row["credits"]
        total_listed = total_listed + ltp["credits"]
        total_hours = total_hours + row["contact_hours_per_week"]
        if not row["matches_table"]:
            note = "calculated " + str(row["credits"]) + " but the table lists " + str(ltp["credits"])
            if ltp["credits"] == 0:
                note = note + " (audit course: it has contact hours but no credits)"
            mismatches.append({"course_code": r["course_code"], "note": note})

    if not courses:
        return {"error": "no courses found for semester " + str(semester) + " (records cover semesters 1-3)"}
    return {
        "semester": semester,
        "courses": len(courses),
        "total_calculated_credits": total_calculated,
        "total_listed_credits": total_listed,
        "total_contact_hours_per_week": total_hours,
        "mismatches": mismatches,
    }


def ltp_credit_calculator(l=None, t=None, p=None, listed_credits=None, semester=None):
    try:
        if semester is not None:
            return calculate_semester(int(semester))
        if l is None or t is None or p is None:
            return {"error": "give l, t and p (hours per week), or give a semester number"}
        return calculate_course(float(l), float(t), float(p), None if listed_credits is None else float(listed_credits))
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print(ltp_credit_calculator(l=3, t=0, p=4, listed_credits=5))
    print(ltp_credit_calculator(semester=1))