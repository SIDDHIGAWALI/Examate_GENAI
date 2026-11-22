# Resume entry: CurriculumBuddy

**CurriculumBuddy: RAG Question Answering over AICTE Engineering Curricula**
*GenAI Course Project · Live demo on Render · GitHub*

- Built a RAG service (FastAPI, ChromaDB, all-MiniLM-L6-v2 embeddings, Groq LLM) over AICTE curriculum PDFs: indexed 612 chunks with source/page citations, enforced "I don't know" refusals for unanswerable questions, and picked the best of 2 chunk-size/top-k configurations on a 15-question evaluation set (<<X>>% answer accuracy, <<Y>>% retrieval hit).
- Designed a tool-using agent in LangGraph with per-thread memory and a human-approval step, plus a deterministic L-T-P credit calculator that caught a curriculum-table inconsistency (Semester 2: 23 listed vs 25 calculated credits); built a Streamlit UI with citations, feedback capture and a prerequisite-chain course card.
- Productionised the service: 80+ pytest tests (input validation, prompt-injection, fake-LLM), ruff, GitHub Actions CI (lint, test, Docker build), Docker Compose and a Render deployment, with per-request latency and token logging, an LLM response cache and request limits (2.8 s median `/ask` latency locally).
- **Tech:** Python, FastAPI, ChromaDB, LangGraph, Streamlit, Docker, GitHub Actions