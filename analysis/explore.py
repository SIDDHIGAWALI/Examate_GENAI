import json
import pandas as pd

with open("data/records.json", encoding="utf-8") as f:
    records = json.load(f)

rows = []
for r in records:
    rows.append({
        "code": r["course_code"],
        "title": r["course_title"],
        "semester": r["semester"],
        "category": r["l_t_p_credits"]["category"],
        "L": r["l_t_p_credits"]["L"],
        "T": r["l_t_p_credits"]["T"],
        "P": r["l_t_p_credits"]["P"],
        "credits": r["l_t_p_credits"]["credits"],
    })
df = pd.DataFrame(rows)

print("Fact 1: total credits per semester")
print(df.groupby("semester")["credits"].sum())

print("\nFact 2: credits per category")
print(df.groupby("category")["credits"].sum().sort_values(ascending=False))

print("\nFact 3: courses where credits do not match L + T + P/2")
df["calculated"] = df["L"] + df["T"] + df["P"] / 2
print(df[df["calculated"] != df["credits"]][["code", "title", "credits", "calculated"]])