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