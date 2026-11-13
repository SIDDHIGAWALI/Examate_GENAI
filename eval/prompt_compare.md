# Prompt comparison: v1 (short) vs v2 (strict rules)

| # | Question | v1 answer (confidence) | v2 answer (confidence) |
|---|----------|------------------------|------------------------|
| 1 | What modules are in the AICTE Operating Systems course and how many hours each? | No course records available for AICTE Operating Systems. (low) | This is not in my data. (low) |
| 2 | Which textbooks does AICTE suggest for Engineering Graphics & Design? | The course record for ESC-102 (Engineering Graphics & Design) does not list any textbooks suggested by AICTE. (low) | This is not in my data. (low) |
| 3 | How many total credits are in the AICTE Mechanical Engineering model curriculum and how are they split by category? | No records for the AICTE Mechanical Engineering model curriculum were found in the provided data. (low) | This is not in my data. (low) |
| 4 | Plan a 13-week schedule for Design and Analysis of Algorithms following the AICTE module hours. | Module hours for Design and Analysis of Algorithms are missing from the records. Unable to plan a 13‑week schedule based on AICTE module hours. (low) | Module hours for Design and Analysis of Algorithms are missing from the records. Unable to create a schedule. (low) |
| 5 | Compare the professional core credits in CSE and ECE model curricula. | No course records available to compare professional core credits for CSE and ECE model curricula. (low) | This is not in my data. (low) |
| 6 | What is the syllabus of Savitribai Phule Pune University for TE Computer 2019 pattern? | No matching course record found. (low) | This is not in my data. (low) |
| 7 | What are the L-T-P and credits of Data Structure and Algorithms? | CS-301: L-T-P: 3-0-4, credits: 5 (high) | L-T-P: 3-0-4, Credits: 5 (high) |
| 8 | Which Semester III courses have a practical (lab) component? | CS-302: IT Workshop (Sci Lab/MATLAB) – branch: CSE, semester: 3, l_t_p_credits: {"L":1,"T":0,"P":4,"credits":3,"category":"PCC"} (high) | CS-302 (high) |
| 9 | What is the total number of credits in Semester II? | 7 (high) | 7 (high) |
| 10 | Which courses in Semesters I-III are audit courses with 0 credits? | No courses in Semesters I-III are audit courses with 0 credits based on the provided records. (high) | This is not in my data. (low) |

## My verdict
## My verdict
v2 (strict rules) is better. It gave the exact answer "This is not in my data." for the questions my
records cannot answer (Q1, Q2, Q3, Q5, Q6) and it was safer on Q10, where v1 wrongly said there are
no audit courses with high confidence. v1 gave a slightly more useful explanation on Q2.
Both prompts failed Q8 and Q9 (e.g. Semester II credits: answered 7, real value 23) because /chat only
passes the top 3 search results to the AI, and these questions need many records. So the weak part is
retrieval, not the prompt. I keep v2 and next I will fix retrieval for counting/total questions.