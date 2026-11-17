import json
import re
import time

from app import rag, vectorstore

CONFIGS = [
    {"name": "A", "chunk_size": 1000, "top_k": 3, "collection": "eval_1000"},
    {"name": "B", "chunk_size": 500, "top_k": 6, "collection": "eval_500"},
]
PAUSE = 2  # seconds between LLM calls, to stay inside the free rate limit

with open("eval/eval_set.json", encoding="utf-8") as f:
    ROWS = json.load(f)


def ensure_index(config):
    collection = vectorstore.get_collection(config["collection"])
    if collection.count() == 0:
        print("Building index for config", config["name"], "(chunk size", config["chunk_size"], ")...")
        vectorstore.index_all(config["chunk_size"], config["collection"])


def retrieved_ok(row, config):
    # did the retrieved chunks contain what we need?
    hits = vectorstore.query(row["question"], k=config["top_k"], name=config["collection"], max_chars=None)
    for h in hits:
        text = (h["title"] + " " + h["text"]).lower()
        for needle in row["must_retrieve"]:
            if needle.lower() in text:
                return True
    return False


def answer_ok(row, result):
    answer = result["answer"]
    if not row["answerable"]:
        return rag.is_unknown(answer)
    if rag.is_unknown(answer) or answer.startswith("LLM call failed"):
        return False
    for pattern in row["expect_all"]:
        if not re.search(pattern, answer, re.IGNORECASE):
            return False
    return True


def run_config(config):
    ensure_index(config)

    rows_out = []
    for row in ROWS:
        start = time.time()
        result = rag.answer(row["question"], config["top_k"], config["collection"])
        if "429" in result["answer"]:               # rate limit: wait once and retry
            time.sleep(20)
            result = rag.answer(row["question"], config["top_k"], config["collection"])
        seconds = time.time() - start

        out = {
            "id": row["id"],
            "answerable": row["answerable"],
            "retrieved": retrieved_ok(row, config) if row["answerable"] else None,
            "correct": answer_ok(row, result),
            "cited": len(result["citations"]) > 0 if row["answerable"] else None,
            "seconds": round(seconds, 1),
            "answer": result["answer"],
        }
        rows_out.append(out)
        print("config", config["name"], "row", row["id"], "correct:", out["correct"])
        time.sleep(PAUSE)
    return rows_out


def percent(part, whole):
    return round(100 * part / whole) if whole else 0


def summarize(config, rows_out):
    answerable = [r for r in rows_out if r["answerable"]]
    unanswerable = [r for r in rows_out if not r["answerable"]]
    return {
        "config": config["name"],
        "chunk_size": config["chunk_size"],
        "top_k": config["top_k"],
        "retrieval": percent(sum(1 for r in answerable if r["retrieved"]), len(answerable)),
        "accuracy": percent(sum(1 for r in rows_out if r["correct"]), len(rows_out)),
        "idk": percent(sum(1 for r in unanswerable if r["correct"]), len(unanswerable)),
        "cited": percent(sum(1 for r in answerable if r["cited"]), len(answerable)),
        "seconds": round(sum(r["seconds"] for r in rows_out) / len(rows_out), 1),
    }


def main():
    summaries = []
    details = {}
    for config in CONFIGS:
        rows_out = run_config(config)
        details[config["name"]] = rows_out
        summaries.append(summarize(config, rows_out))

    # winner = best answer accuracy, then best retrieval, then smaller context
    winner = sorted(summaries, key=lambda s: (-s["accuracy"], -s["retrieval"], s["chunk_size"] * s["top_k"]))[0]

    table = ["| Config | Chunk size | Top-k | Retrieval hit | Answer accuracy | Correct \"I don't know\" | Cited | Avg seconds |",
             "|---|---|---|---|---|---|---|---|"]
    for s in summaries:
        mark = " (winner)" if s is winner else ""
        table.append(f"| {s['config']}{mark} | {s['chunk_size']} | {s['top_k']} | {s['retrieval']}% | {s['accuracy']}% | "
                     f"{s['idk']}% | {s['cited']}% | {s['seconds']} |")
    table_text = "\n".join(table)

    per_row = ["| # | Question | Answerable | A correct | B correct |", "|---|---|---|---|---|"]
    for i, row in enumerate(ROWS):
        a = details["A"][i]["correct"]
        b = details["B"][i]["correct"]
        per_row.append(f"| {row['id']} | {row['question']} | {row['answerable']} | {'yes' if a else 'NO'} | {'yes' if b else 'NO'} |")

    report = "# Evaluation results\n\n" + table_text + "\n\nWinner: config " + winner["config"] + "\n\n" + "\n".join(per_row) + "\n"
    with open("eval/results.md", "w", encoding="utf-8") as f:
        f.write(report)
    with open("eval/results.json", "w", encoding="utf-8") as f:
        json.dump({"summaries": summaries, "details": details}, f, indent=2)

    # put the table into README.md between two markers
    section = ("<!-- EVAL:START -->\n## Evaluation (15 questions, 2 configs)\n\n" + table_text +
               f"\n\nWinner: config {winner['config']} (chunk size {winner['chunk_size']}, top-k {winner['top_k']}). "
               "Details: `eval/results.md`.\n<!-- EVAL:END -->")
    with open("README.md", encoding="utf-8") as f:
        readme = f.read()
    if "<!-- EVAL:START -->" in readme:
        readme = re.sub(r"<!-- EVAL:START -->.*<!-- EVAL:END -->", lambda m: section, readme, flags=re.DOTALL)
    else:
        readme = readme.rstrip() + "\n\n" + section + "\n"
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)
    print(table_text)
    print("Winner: config", winner["config"])


if __name__ == "__main__":
    main()