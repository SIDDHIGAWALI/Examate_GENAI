import json
from dataclasses import asdict
from pypdf import PdfReader
from app.models import Record

# 1. read the PDF into a list of text lines
lines = []
reader = PdfReader("data/raw/Updated-AICTE_-_UG_CSE.pdf")
for page in reader.pages:
    lines = lines + page.extract_text().splitlines()

# 2. find the table rows of Semester I, II, III
records = []
bad_rows = 0
semester = 0
row = ""

for line in lines:
    line = line.strip()

    if line == "Semester I":
        semester = 1
    elif line == "Semester II":
        semester = 2
    elif line == "Semester III":
        semester = 3
    elif line == "Semester IV" and semester == 3:
        break
    elif semester > 0:
        if line[:1].isdigit() and "." in line[:3]:
            row = line                  # a new row starts, like "1. BSC-101 Physics-I 3 1 2 5"
        elif row != "":
            row = row + " " + line      # title continues on the next line

        words = row.split()
        if len(words) > 4 and words[-1].isdigit() and words[-4].isdigit():
            # 3. the row is complete, make a record
            try:
                l = int(words[-4])
                t = int(words[-3])
                p = int(words[-2])
                credits = int(words[-1])
                middle = words[1:-4]
                category = ""
                if middle[0] == "PCC":
                    category = "PCC"
                    middle = middle[1:]
                code = middle[0].replace("^", "")
                title = " ".join(middle[1:])
                if category == "":
                    category = code.split("-")[0].split("(")[0]
                ltp = {"L": l, "T": t, "P": p, "credits": credits, "category": category}
                records.append(Record(code, title, "CSE", semester, ltp, []))
            except Exception:
                bad_rows = bad_rows + 1
                print("Skipped:", row)
            row = ""

# 4. save
with open("data/records.json", "w") as f:
    json.dump([asdict(r) for r in records], f, indent=2)
print("Saved", len(records), "records,", bad_rows, "skipped")