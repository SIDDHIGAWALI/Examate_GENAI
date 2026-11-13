import json
from app.chat import chat

with open("data/records.json", encoding="utf-8") as f:
    records = json.load(f)

QUESTIONS = [
    "What modules are in the AICTE Operating Systems course and how many hours each?",
    "Which textbooks does AICTE suggest for Engineering Graphics & Design?",
    "How many total credits are in the AICTE Mechanical Engineering model curriculum and how are they split by category?",
    "Plan a 13-week schedule for Design and Analysis of Algorithms following the AICTE module hours.",
    "Compare the professional core credits in CSE and ECE model curricula.",
    "What is the syllabus of Savitribai Phule Pune University for TE Computer 2019 pattern?",
    "What are the L-T-P and credits of Data Structure and Algorithms?",
    "Which Semester III courses have a practical (lab) component?",
    "What is the total number of credits in Semester II?",
    "Which courses in Semesters I-III are audit courses with 0 credits?",
]

lines = ["# Prompt comparison: v1 (short) vs v2 (strict rules)", ""]
lines.append("| # | Question | v1 answer (confidence) | v2 answer (confidence) |")
lines.append("|---|----------|------------------------|------------------------|")
for i, q in enumerate(QUESTIONS, start=1):
    a1 = chat(records, q, "v1")
    a2 = chat(records, q, "v2")
    t1 = a1["answer"].replace("\n", " ").replace("|", "/")
    t2 = a2["answer"].replace("\n", " ").replace("|", "/")
    lines.append(f"| {i} | {q} | {t1} ({a1['confidence']}) | {t2} ({a2['confidence']}) |")
    print("done", i)

lines.append("")
lines.append("## My verdict")
lines.append("(write 3-4 lines here: which prompt invented fewer facts, which said 'not in my data' for Q6, which one you keep)")

with open("eval/prompt_compare.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Saved eval/prompt_compare.md")