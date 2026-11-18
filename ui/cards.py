import html
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

# colours for the module bars (mid tones, dark text stays readable on all of them)
COLOURS = ["#8fb8ff", "#ffb86b", "#9be3a6", "#f0a4d4", "#c7b3ff", "#ffe17a", "#7fdcd6", "#ff9e9e"]


def load_records():
    with open(DATA / "records.json", encoding="utf-8") as f:
        return json.load(f)


def load_cards():
    with open(DATA / "course_cards.json", encoding="utf-8") as f:
        return json.load(f)


def number_text(value):
    return str(int(value)) if float(value) == int(value) else str(value)


def duration_text(value, unit):
    # "1 week", "2.5 weeks"
    if value == 1:
        unit = unit.rstrip("s")
    return number_text(value) + " " + unit


def prerequisite_paths(code, cards, by_code):
    # every chain that leads to this course, earliest course first, e.g. [["BSC-102", "BSC-201", "BSC-301"]]
    paths = []
    for p in cards.get(code, {}).get("prerequisites", []):
        before = p["code"]
        if before not in by_code:
            continue
        if by_code[before]["semester"] >= by_code[code]["semester"]:
            continue                     # only courses from an EARLIER semester count
        for path in prerequisite_paths(before, cards, by_code) or [[before]]:
            paths.append(path + [code])
    return paths


def prerequisite_notes(code, cards, by_code):
    # one line per link in the chain: where the link comes from (AICTE text or my own inference)
    notes = []
    seen = set()
    for path in prerequisite_paths(code, cards, by_code):
        for before, after in zip(path, path[1:]):
            if (before, after) in seen:
                continue
            seen.add((before, after))
            basis = ""
            for p in cards[after]["prerequisites"]:
                if p["code"] == before:
                    basis = p["basis"]
            notes.append(before + " -> " + after + ": " + basis)
    return notes


def module_strip(modules):
    # decide how to draw the bars
    if not modules:
        return {"mode": "none", "segments": [], "total": None, "unit": None}

    all_have_hours = all(m["hours"] for m in modules)
    units = set(m["unit"] for m in modules if m["hours"])

    segments = []
    if all_have_hours and len(units) == 1:
        total = sum(m["hours"] for m in modules)
        for i, m in enumerate(modules, start=1):
            segments.append({
                "number": i, "name": m["name"], "percent": 100 * m["hours"] / total,
                "label": duration_text(m["hours"], m["unit"]),
            })
        return {"mode": "proportional", "segments": segments, "total": total, "unit": units.pop()}

    for i, m in enumerate(modules, start=1):
        label = "duration not stated"
        if m["hours"]:
            label = duration_text(m["hours"], m["unit"])
        segments.append({"number": i, "name": m["name"], "percent": 100 / len(modules), "label": label})
    return {"mode": "equal", "segments": segments, "total": None, "unit": None}


def strip_html(strip):
    if strip["mode"] == "none":
        return ""
    parts = ['<div style="display:flex;width:100%;height:46px;border-radius:8px;overflow:hidden;'
             'border:1px solid rgba(128,128,128,.5);">']
    for s in strip["segments"]:
        colour = COLOURS[(s["number"] - 1) % len(COLOURS)]
        tip = html.escape("M" + str(s["number"]) + " " + s["name"] + " (" + s["label"] + ")")
        text = "M" + str(s["number"])
        if strip["mode"] == "proportional" and s["percent"] >= 9:
            text = text + " · " + html.escape(s["label"].split(" ")[0])
        parts.append('<div title="' + tip + '" style="flex:' + str(round(s["percent"], 2)) + ' 1 0;background:' + colour +
                     ';color:#14161a;display:flex;align-items:center;justify-content:center;font-size:13px;'
                     'font-weight:600;border-right:1px solid rgba(0,0,0,.25);white-space:nowrap;">' + text + '</div>')
    parts.append("</div>")
    return "".join(parts)


def legend_html(strip):
    rows = []
    for s in strip["segments"]:
        colour = COLOURS[(s["number"] - 1) % len(COLOURS)]
        rows.append('<div style="margin:3px 0;"><span style="display:inline-block;width:12px;height:12px;border-radius:3px;'
                    'background:' + colour + ';margin-right:8px;vertical-align:middle;"></span>'
                    '<b>M' + str(s["number"]) + '</b> ' + html.escape(s["name"]) +
                    ' <span style="opacity:.7;">— ' + html.escape(s["label"]) + '</span></div>')
    return "".join(rows)


def chain_html(paths, code, by_code):
    if not paths:
        return ""
    blocks = []
    for path in paths:
        boxes = []
        for c in path:
            r = by_code[c]
            selected = (c == code)
            style = ("border:2px solid #4c8dff;background:rgba(76,141,255,.15);" if selected
                     else "border:1px solid rgba(128,128,128,.6);")
            boxes.append('<div style="' + style + 'border-radius:8px;padding:8px 12px;min-width:130px;">'
                         '<div style="font-size:12px;opacity:.7;">Semester ' + str(r["semester"]) + '</div>'
                         '<div style="font-weight:700;">' + html.escape(c) + '</div>'
                         '<div style="font-size:13px;">' + html.escape(r["course_title"]) + '</div></div>')
        blocks.append('<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:8px 0;">' +
                      '<div style="font-size:22px;opacity:.6;">→</div>'.join(boxes) + '</div>')
    return "".join(blocks)