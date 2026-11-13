import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://api.groq.com/openai/v1/models"
headers = {"Authorization": "Bearer " + os.getenv("GROQ_API_KEY", "")}
response = requests.get(url, headers=headers, timeout=30)
print("Status:", response.status_code)

if response.status_code == 200:
    for m in response.json()["data"]:
        print(m["id"])
else:
    print(response.text[:300])