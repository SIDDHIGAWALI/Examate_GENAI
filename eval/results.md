# Evaluation results

| Config | Chunk size | Top-k | Retrieval hit | Answer accuracy | Correct "I don't know" | Cited | Avg seconds |
|---|---|---|---|---|---|---|---|
| A | 1000 | 3 | 64% | 47% | 100% | 45% | 2.6 |
| B (winner) | 500 | 6 | 82% | 47% | 100% | 55% | 9.1 |

Winner: config B

| # | Question | Answerable | A correct | B correct |
|---|---|---|---|---|
| 1 | What modules are in the AICTE Operating Systems course and how long is each? | True | NO | NO |
| 2 | Which textbook does AICTE prescribe for Engineering Graphics & Design? | True | yes | NO |
| 3 | How many total credits are in the AICTE Mechanical Engineering model curriculum? | True | yes | yes |
| 4 | Plan a 13-week schedule for Design and Analysis of Algorithms following the AICTE module durations. | True | NO | NO |
| 5 | Compare the professional core credits in CSE and ECE model curricula. | False | yes | yes |
| 6 | What is the syllabus of Savitribai Phule Pune University for TE Computer 2019 pattern? | False | yes | yes |
| 7 | What are the L-T-P and credits of Data Structure and Algorithms? | True | NO | NO |
| 8 | Which Semester III courses in the CSE curriculum have a practical (lab) component? | True | NO | NO |
| 9 | What is the total number of credits in Semester II of the CSE curriculum? | True | NO | NO |
| 10 | Which courses in Semesters I-III of the CSE curriculum are audit courses with 0 credits? | True | NO | NO |
| 11 | How many credits does Machine Learning (CS-603) carry in the CSE curriculum? | True | yes | yes |
| 12 | What is the course code of Computer Networks in the CSE curriculum? | True | NO | NO |
| 13 | How many hours is Module 3 (Sequences and series) of Mathematics-I? | True | NO | yes |
| 14 | What is the annual tuition fee at Sanjivani University? | False | yes | yes |
| 15 | Which faculty member teaches Design and Analysis of Algorithms at Sanjivani this semester? | False | yes | yes |
