# CurriculumBuddy: interview notes

## 60-second pitch
CurriculumBuddy answers questions about the AICTE model curriculum, built for a new assistant professor who has to prepare a course plan. The curriculum PDFs are very long, full of tables and module lists, so finding one course's L-T-P, credits and modules is slow and easy to get wrong.

I built a FastAPI service that indexes 612 chunks in ChromaDB, retrieves the right ones and answers with citations to the file, page and course. If the documents don't contain the answer, it says "I don't know"; in my 15-question evaluation it refused correctly every time. On top of that, a LangGraph agent has a credit calculator that applies the AICTE rule, credits = L + T + P/2, and it caught that Semester 2 lists 23 credits while the hours add up to 25, because of an audit course.

It has 80+ tests, CI, Docker and a live deployment on Render. The honest weak spot is answer accuracy: 47% on my evaluation. That is what I would improve next.

## My hardest problem: structure in very long PDFs
**Problem.** In these PDFs the structure carries the meaning. A course's title, L-T-P, modules and outcomes belong together, and the credit tables have to be read as rows of data. Fixed-size chunking cuts a course in half, and a naive table read splits a row when a long course title wraps onto the next line.

**What I did.**
- **Section-aware chunking.** I split the text by course heading, found with the `L:T:P` pattern. My first version assigned wrong course titles because the course code can sit one to three lines above the heading when the title wraps. I fixed it by looking back up to three lines for the code and resetting the title at each "SEMESTER" line, so a chunk keeps its title, L-T-P and modules together and carries its source file and page.
- **Tables as data.** For the credit table I join wrapped lines until a row ends with its four numbers (L, T, P, credits), then parse it into a record. Bad rows go through try/except and are counted, not silently dropped. Result: 19 course records, 0 skipped.
- **Stale index.** I found old chunks surviving a re-index, so indexing now deletes and rebuilds the collection.

**What I learned.** Check the data before tuning the model. Most of my early wrong answers came from bad chunks, not from the LLM.

## 10 likely questions

**1. Walk me through the architecture.**
Offline, `ingest.py` turns the PDFs into 19 course records, and `chunking.py` plus MiniLM embeddings build a Chroma index of 612 chunks. Online, a FastAPI service handles requests: `/ask` retrieves chunks, asks the Groq LLM and returns an answer with citations, and `/agent` runs a LangGraph agent that can call RAG search and a credit calculator. A Streamlit UI sits on top. A middleware layer adds input limits, latency and token logging, and a cache.

**2. What was the hardest problem?**
See "My hardest problem" above: keeping each course's title, L-T-P, modules and outcomes together through section-aware chunking, and extracting the credit tables as rows of data.

**3. Why chunk by course instead of fixed size?**
A fixed-size chunk can cut a course in two, so the chunk with the modules has no course title or L-T-P, and retrieval returns text that cannot be attributed. Chunking by course heading keeps the facts that belong together, and each chunk carries its source and page for citations. The cost is that it depends on the heading pattern of these particular PDFs.

**4. How do you stop the model from making things up?**
The prompt says to answer only from the numbered chunks, cite them as `[n]`, and otherwise say "I don't know based on the documents." I measured it: 100% correct refusals on my evaluation set for both configurations. I also learned that the similarity score alone cannot separate answerable from unanswerable questions, so I rely on the prompt rule and I test it.

**5. How did you evaluate it, and why is accuracy only 47%?**
15 questions, 2 configurations. Config A (chunk size 1000, top-3): 64% retrieval hit, 47% answer accuracy. Config B (chunk size 500, top-6): 82% retrieval hit, 47% answer accuracy, 55% of answers cited. B won on retrieval and citations; the accuracy was the same. Accuracy is the weak point. I have not yet separated real wrong answers from checks that are too strict about formatting, so 47% is a conservative number; the next step is a manual re-grade and fixing the real misses.

**6. Why ChromaDB with MiniLM, and why also keep keyword search?**
MiniLM (all-MiniLM-L6-v2) is small, free and runs on a laptop, which suits a student project and a 512 MB server. Chroma gives a persistent local index with no extra service. I kept TF-IDF search because exact course codes and numbers are matched well by keywords, while semantic search handles paraphrased questions.

**7. Why does the agent use a calculator tool instead of letting the LLM do the maths?**
LLMs make arithmetic mistakes, and credits must be exact. The tool applies the AICTE rule (credits = L + T + P/2) in code and compares it with the table. It found that Semester 2 lists 23 credits but the hours calculate to 25, because audit courses such as AU-102 have contact hours but 0 credits. A table inconsistency like that is exactly what a professor would want flagged.

**8. How does the approval step work?**
The agent is a LangGraph graph with nodes for deciding, approval, running tools and finishing. Before the first tool call the graph pauses with `interrupt` and waits for the user to approve or reject. A `MemorySaver` checkpoint keeps the state per thread, so the same conversation can resume with the answer. In the UI this is the Approve / Reject box. Once approved for a question, later tool calls for that question run without asking again.

**9. How do you handle prompt injection, abuse and cost?**
User text only ever goes into the user message, never into the system prompt, and a test checks that. The agent can only run tools from a fixed list; an unknown tool or invalid arguments return an error and nothing is executed. Requests are limited: body over 10 KB returns 413, and a question over 500 characters or empty returns 422, checked before any LLM call. An in-memory cache avoids repeating identical LLM calls, and each request logs latency and estimated tokens (about 950 tokens in per call).

**10. What went wrong when you deployed, and what would you change?**
Three things. My first Render build downloaded the PDFs from aicte.gov.in, and AICTE returned 403 to Render's servers, so I committed the PDFs and build the index inside the image. A Groq model replied in tool-call format and got a 400 error, so I tightened the prompt and added recovery for that case. On Render's free tier (0.1 CPU, 512 MB) `/ask` takes about 8.8 s against 2.8 s on my laptop, because embedding the question is slow there. With more time I would cache retrieval results, re-grade the evaluation by hand to improve accuracy, use exact token counts from the provider, and move to a bigger instance.

## Numbers to remember
- 19 course records, 612 chunks, 81 tests
- Evaluation: 15 questions, 100% correct refusals, 47% answer accuracy, retrieval hit 64% (A) vs 82% (B)
- Semester 2: 23 credits listed vs 25 calculated (audit course AU-102)
- `/ask` median: 2.8 s locally, 8.8 s on Render's free tier