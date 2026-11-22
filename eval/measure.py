import sys
import time

import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
QUESTIONS = [
    "What are the L-T-P and credits of Data Structure and Algorithms?",
    "How many credits does Mathematics-II have?",
    "What is the course code for Digital Electronics?",
    "What is the category of Engineering Graphics and Design?",
    "What is the syllabus of Savitribai Phule Pune University?",
    "What is the L-T-P of Basic Electrical Engineering?",
]


def post_ms(question):
    start = time.perf_counter()
    r = requests.post(BASE + "/ask", json={"question": question}, timeout=120)
    return (time.perf_counter() - start) * 1000, r.status_code


def median(values):
    values = sorted(values)
    return values[len(values) // 2]


def health_ms():
    start = time.perf_counter()
    requests.get(BASE + "/health", timeout=60)
    return (time.perf_counter() - start) * 1000


requests.get(BASE + "/health", timeout=120)          # wake the server up first
health = [health_ms() for _ in range(20)]

first = []
for q in QUESTIONS:
    ms, status = post_ms(q)
    print("first call ", status, round(ms), "ms -", q[:50])
    first.append(ms)
    time.sleep(2)                                    # be gentle with the rate limit

repeat = []
for q in QUESTIONS:
    ms, status = post_ms(q)
    print("repeat call", status, round(ms), "ms -", q[:50])
    repeat.append(ms)

resp = requests.get(BASE + "/metrics", timeout=30)
stats = resp.json() if resp.status_code == 200 else {}
ask = stats.get("paths", {}).get("/ask", {})

print()
print("| Measurement | Value |")
print("|---|---|")
print("| /health median latency | " + str(round(median(health))) + " ms |")
print("| /ask first call, median of " + str(len(first)) + " | " + str(round(median(first))) + " ms |")
print("| /ask first call, slowest | " + str(round(max(first))) + " ms |")
print("| /ask repeat (cached LLM), median | " + str(round(median(repeat))) + " ms |")
print("| avg tokens in per LLM call (est.) | " + str(ask.get("avg_tokens_in", "n/a")) + " |")
print("| avg tokens out per LLM call (est.) | " + str(ask.get("avg_tokens_out", "n/a")) + " |")
print("| cache hit rate (each question asked twice) | " + str(stats.get("cache_hit_rate", "n/a")) + " |")