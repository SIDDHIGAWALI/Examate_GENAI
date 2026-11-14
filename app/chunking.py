import os
import re
from pypdf import PdfReader

RAW_FOLDER = "data/raw"
MAX_CHARS = 1000

LTP = re.compile(r"\dL:\dT:\dP")                             # 3L:1T:2P
CODE = re.compile(r"^[A-Z]{2,5}[\s-]*[A-Z]*[\s-]*\d{2,3}")   # BSC-101, PCC CS-301, PCC-ME 202
SEMESTER = re.compile(r"^semester\b", re.IGNORECASE)         # SEMESTER II


def chunk_pdf(path, max_chars=MAX_CHARS):
    source = os.path.basename(path)
    doc_title = source.replace(".pdf", "").replace("_", " ")
    reader = PdfReader(path)

    chunks = []
    title = doc_title      # title of the course we are inside
    pending = []           # lines of the current chunk, as (text, page)

    def save_chunk():
        nonlocal pending
        text = "\n".join(line for line, page in pending).strip()
        if len(text) > 30:
            chunks.append({
                "id": source + "-" + str(len(chunks) + 1),
                "text": text,
                "source": source,
                "page": pending[0][1],
                "title": title,
            })
        pending = []

    for page_number, page in enumerate(reader.pages, start=1):
        for line in (page.extract_text() or "").splitlines():
            line = line.strip()
            if line == "":
                continue

            if LTP.search(line):
                # a course heading. The course code and name may be on the 1-3 lines before it
                k = 0
                if not CODE.match(line):
                    for n in (1, 2, 3):
                        if len(pending) >= n and CODE.match(pending[-n][0]):
                            k = n
                            break
                moved = pending[len(pending) - k:] if k > 0 else []
                pending = pending[:len(pending) - k] if k > 0 else pending
                save_chunk()                       # close the chunk of the previous course
                pending = moved
                title = " ".join(text for text, p in moved + [(line, page_number)])
            elif SEMESTER.match(line) and len(line) < 25:
                save_chunk()                       # a new semester starts, no course yet
                title = doc_title

            pending.append((line, page_number))
            if sum(len(text) + 1 for text, p in pending) >= max_chars:
                save_chunk()
    save_chunk()
    return chunks


def chunk_all(folder=RAW_FOLDER):
    all_chunks = []
    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith(".pdf"):
            continue
        try:
            found = chunk_pdf(os.path.join(folder, name))
            print(name, "->", len(found), "chunks")
            all_chunks = all_chunks + found
        except Exception as e:
            print("Skipped", name, "-", e)
    return all_chunks


if __name__ == "__main__":
    chunks = chunk_all()
    print("Total chunks:", len(chunks))
    titles = sorted(set(c["title"] for c in chunks))
    print("Different titles:", len(titles))
    for t in titles:
        print(" -", t)