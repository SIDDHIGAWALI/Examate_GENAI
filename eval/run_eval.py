import json, os, sys, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.vectorstore import query as vs_query, get_collection
from app.llm import ask_llm

with open("eval/eval_set.json", encoding="utf-8") as f:
    EVAL = json.load(f)

SYSTEM = """You are CurriculumBuddy. Answer ONLY from the CONTEXT CHUNKS below.
If the chunks do not contain the answer, say exactly: "I don't know."
Never invent facts. Keep it short.
Reply as JSON: {"answer": "..."}"""

CONFIGS = [
    {"name": "k=3", "k": 3},
    {"name": "k=5", "k": 5},
]


def get_answer(question, k):
    hits = vs_query(question, k=k)
    ctx = ""
    for i, h in enumerate(hits, 1):
        ctx += f"[{i}] {h['source']} p{h['page']}\n{h['text']}\n\n"
    raw = ask_llm(SYSTEM, f"QUESTION: {question}\n\nCONTEXT CHUNKS:\n{ctx}")
    clean = raw.strip().strip("`")
    if clean.lower().startswith("json"):
        clean = clean[4:]
    try:
        return json.loads(clean).get("answer", clean)
    except Exception:
        return clean


def check(answer, row):
    low = answer.lower()
    if not row["answerable"]:
        return 1 if "don't know" in low or "do not know" in low or "not in my data" in low else 0
    words = row["expected"].lower().split()
    found = sum(1 for w in words if w in low)
    return round(found / len(words), 2)


def run(config):
    print(f"\n--- {config['name']} ---")
    results = []
    for row in EVAL:
        try:
            ans = get_answer(row["question"], config["k"])
        except Exception as e:
            ans = f"ERROR: {e}"
        s = check(ans, row)
        results.append({"id": row["id"], "q": row["question"][:50], "expected": row["expected"], "got": ans[:80], "score": s})
        print(f"  {row['id']}: {s}")
        time.sleep(1)
    return results


if get_collection().count() == 0:
    print("Index empty! Run: python -m app.vectorstore")
    sys.exit(1)

all_runs = {}
for cfg in CONFIGS:
    all_runs[cfg["name"]] = run(cfg)

# pick winner
best_name, best_avg = "", 0
for name, res in all_runs.items():
    avg = sum(r["score"] for r in res) / len(res)
    print(f"\n{name} avg = {avg:.2f}")
    if avg >= best_avg:
        best_avg, best_name = avg, name

# append winner table to README
winner = all_runs[best_name]
lines = [
    "\n\n## RAG Evaluation (Sprint 2)",
    f"\n**Winner: {best_name}** — Avg Score: **{best_avg:.2f}**\n",
    "| ID | Question | Expected | Got | Score |",
    "|----|----------|----------|-----|-------|",
]
for r in winner:
    lines.append(f"| {r['id']} | {r['q']} | {r['expected'][:30]} | {r['got'][:40].replace(chr(10),' ')} | {r['score']} |")

with open("README.md", "a", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\nWinner: {best_name} ({best_avg:.2f}) → appended to README.md")




