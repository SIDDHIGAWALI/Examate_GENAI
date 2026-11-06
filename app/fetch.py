import os
import requests

URLS = [
    "https://www.aicte.gov.in/sites/default/files/Updated-AICTE%20-%20UG%20CSE.pdf",
    "https://aicte.gov.in/sites/default/files/Final_Mechanical%20Engg.pdf",
    "https://www.iiitd.ac.in/sites/default/files/docs/about/AICTE2018-CSE-Curriculum.pdf",
    "https://www.osmania.ac.in/oldsite/Syllabus_2019/Engineering_2020_2021/UG-CSE/BE-(CSE)-AICTEMODEL-SCHEME2018-19.pdf",
    "https://www.ietlucknow.ac.in/sites/default/files/mag/Syllabus%20CSE.pdf",
]

HEADERS = {"User-Agent": "Mozilla/5.0"}


def download(url, folder="data/raw"):
    os.makedirs(folder, exist_ok=True)
    name = url.split("/")[-1].replace("%20", "_")
    path = os.path.join(folder, name)
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)
        print("Saved:", path)
    except requests.exceptions.Timeout:
        print("Timeout:", url)
    except requests.exceptions.RequestException as e:
        print("Failed:", url, "-", e)


if __name__ == "__main__":
    for url in URLS:
        download(url)