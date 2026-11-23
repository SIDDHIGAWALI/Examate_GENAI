# PROGRESS

## Done (evidence)
- [x] Day 1: repo, README project card, `day01_intro.py`, `day01_menu.py`
- [x] Day 2: course records (`data/sample_records.py`), `app/records.py`, `app/cli.py`, `.gitignore`, `requirements.txt`
- [x] Day 3: `app/ingest.py` (19 records, 0 skipped), `app/models.py`, `app/fetch.py`
- [x] Week 1: FastAPI service, TF-IDF search (`smart_search.py`), `analysis/explore.py`
- [x] Checkpoint 1: `docs/how_llms_work.md`, 10 questions
- [x] LLM: `app/llm.py`, `/chat`, prompts, prompt comparison, `.env.example`
- [x] Semantic search: chunking, embeddings, Chroma (612 chunks), `/search/semantic`
- [x] RAG: `/ask` with citations; eval of 2 configs (config B: 82% retrieval hit, 47% accuracy, 100% correct "I don't know")
- [x] Agent: `ltp_credit_calculator`, hand-written loop, LangGraph with approval, `/agent`
- [x] UI: Streamlit chat, feedback, course card
- [x] Tests: 81 passed; `ruff check .` passes
- [x] Docker: Dockerfile, compose, tested with `docker compose up`
- [x] CI: GitHub Actions (ruff, pytest, docker build), badge, PR merged
- [x] Deploy: https://curriculumbuddy.onrender.com (`/health` works)
- [x] Production: latency and token logging, cache, input limits, injection test, measured numbers in README
- [x] README with architecture diagram, results table, production notes; `docs/resume.md`

## Open (to close)
- [ ] Tags `week-1`, `checkpoint-1`, `checkpoint-2` exist on GitHub (`git ls-remote --tags origin`)
- [ ] UI screenshots `docs/ui_chat.png` and `docs/ui_card.png` pushed
- [ ] Demo video recorded; link in README
- [ ] Live URL and video link in the tracker
- [ ] `docs/interview.md` merged
- [ ] Chroma index untracked in git (`git rm -r --cached data/chroma`)
- [ ] Repo name confirmed with the teacher (`git remote -v`)
- [ ] Demo rehearsed twice
- [ ] Tag `final` pushed