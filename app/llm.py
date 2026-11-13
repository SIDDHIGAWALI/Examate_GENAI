import os
import requests
from dotenv import load_dotenv

load_dotenv()  # reads the .env file


def check(response):
    if response.status_code != 200:
        raise RuntimeError(str(response.status_code) + " " + response.text[:300])


def ask_groq(system, user):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": "Bearer " + os.getenv("GROQ_API_KEY", "")}
    body = {
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
    }
    response = requests.post(url, headers=headers, json=body, timeout=30)
    check(response)
    return response.json()["choices"][0]["message"]["content"]


def ask_gemini(system, user):
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent"
    headers = {"x-goog-api-key": os.getenv("GEMINI_API_KEY", "")}
    body = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": 0.2},
    }
    response = requests.post(url, headers=headers, json=body, timeout=30)
    check(response)
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


def ask_llm(system, user):
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    if provider == "gemini":
        return ask_gemini(system, user)
    return ask_groq(system, user)