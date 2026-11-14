from app.chunking import chunk_all
from app.embed import chunk_to_text, embed_texts, semantic_search

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

chunks = chunk_all()
print("Embedding", len(chunks), "chunks (first run downloads the model)...")
vectors = embed_texts([chunk_to_text(c) for c in chunks])

lines = ["# Semantic search results", ""]
lines.append("Chunks searched: " + str(len(chunks)) + ". Top 3 hits per question.")
for number, question in enumerate(QUESTIONS, start=1):
    lines.append("")
    lines.append("## Q" + str(number) + ". " + question)
    for rank, hit in enumerate(semantic_search(chunks, vectors, question, k=3), start=1):
        c = hit["chunk"]
        snippet = c["text"][:200].replace("\n", " ")
        lines.append(f"{rank}. score {hit['score']} | {c['source']} | page {c['page']} | {c['title']}")
        lines.append("   > " + snippet)
    lines.append("")
    lines.append("**Relevant? (yes / partly / no):** ")
    print("done", number)

with open("eval/search_results.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Saved eval/search_results.md")