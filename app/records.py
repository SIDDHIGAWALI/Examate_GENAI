from data.sample_records import RECORDS


def load_records():
    return RECORDS


def search(records, keyword):
    found = []
    for r in records:
        if keyword.lower() in r["course_title"].lower():
            found.append(r)
    return found


def count_by(records, field):
    counts = {}
    for r in records:
        key = r[field]
        if key in counts:
            counts[key] = counts[key] + 1
        else:
            counts[key] = 1
    return counts


def get_by_id(records, course_code):
    for r in records:
        if r["course_code"] == course_code:
            return r
    return None