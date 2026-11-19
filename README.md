# sanjivani-sj-27-curriculumbuddy

# CurriculumBuddy

## Product
Q&A over AICTE model curricula for UG engineering: course contents module by module, L-T-P and credits, prerequisites, outcomes and suggested textbooks.

## User
A newly joined assistant professor in the Computer Engineering department at Sanjivani who must prepare a course plan for "Design and Analysis of Algorithms" aligned with the AICTE model curriculum.

## Problem
Course details are buried in very long AICTE PDFs with course tables, module lists and book lists, making it slow to find modules, credits and prerequisites for a course plan.

## Data Source
- AICTE UG CSE model curriculum (PDF): https://www.aicte.gov.in/sites/default/files/Updated-AICTE%20-%20UG%20CSE.pdf
- AICTE Mechanical Engineering model curriculum (PDF): https://aicte.gov.in/sites/default/files/Final_Mechanical%20Engg.pdf




## How to run
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m app.fetch        # download PDFs into data/raw/
python -m app.ingest       # build data/records.json
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs to try the API.

Endpoints: `GET /health`, `GET /records?limit=`, `GET /records/{course_code}`, `GET /search?q=`, `POST /questions`

Data exploration: `python -m analysis.explore`

## RAG Evaluation (Sprint 2)

**Winner: k=5** — Avg Score: **0.41**

| ID | Question | Expected | Got | Score |
|----|----------|----------|-----|-------|
| Q1 | What are the L-T-P and credits of Data Structure a | L=3 T=0 P=4 Credits=5 | L‑T‑P: 3L:0T:4P, Credits: 5 | 0.0 |
| Q2 | Which semester is Data Structure and Algorithms in | Semester 3 | I don't know. | 0.0 |
| Q3 | What is the category of Mathematics-I? | BSC | I don't know. | 0.0 |
| Q4 | How many credits does Engineering Graphics and Des | 3 | 3 | 1.0 |
| Q5 | Which Semester III courses have a practical compon | Analog Electronic Circuits, Da | KEE201/ KCS201 Basic Electrical Engineer | 0.0 |
| Q6 | What is the syllabus of Savitribai Phule Pune Univ | I don't know | I don't know. | 1 |
| Q7 | What is the total number of credits in Semester II | 23 | I don't know. | 0.0 |
| Q8 | Which courses are audit courses with 0 credits? | AU-101 IDEA Lab Workshop and A | ERROR: 429 {"error":{"message":"Rate lim | 0.22 |
| Q9 | What is the L-T-P of Basic Electrical Engineering? | L=3 T=1 P=2 | 3L:1T:2P | 0.0 |
| Q10 | How many credits does Mathematics-II have? | 4 | ERROR: 429 {"error":{"message":"Rate lim | 1.0 |
| Q11 | What is the course code for Digital Electronics? | ESC-302 | ESC-302 | 1.0 |
| Q12 | Which branch is Programming for Problem Solving in | CSE | Computer Science and Engineering | 0.0 |
| Q13 | What is the GATE syllabus for Computer Science? | I don't know | I don't know. | 1 |
| Q14 | How many courses are in Semester I? | 6 | ERROR: 429 {"error":{"message":"Rate lim | 1.0 |
| Q15 | What is the category of IT Workshop? | PCC | I don't know. | 0.0 |

<!-- EVAL:START -->
## Evaluation (15 questions, 2 configs)

| Config | Chunk size | Top-k | Retrieval hit | Answer accuracy | Correct "I don't know" | Cited | Avg seconds |
|---|---|---|---|---|---|---|---|
| A | 1000 | 3 | 64% | 0% | 0% | 0% | 0.6 |
| B (winner) | 500 | 6 | 82% | 0% | 0% | 0% | 0.6 |

Winner: config B (chunk size 500, top-k 6). Details: `eval/results.md`.
<!-- EVAL:END -->

## Tests

Run all tests from the project root:

```
python -m pytest -q
```

28 tests cover:
- the L-T-P credit calculator: AICTE mapping, semester totals, audit-course mismatches and input validation
- the agent: tool calling, unknown tools, the 5-step limit, LLM failure, and the LangGraph approval step, rejection and per-thread memory

The agent tests use a fake LLM, so they need no API key and no internet.

## Run with Docker
...
Status: Dockerfile and compose written; the image build was blocked by network timeouts on my machine, so the full run is untested.