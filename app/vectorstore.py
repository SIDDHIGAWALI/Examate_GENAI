import chromadb
from app import embed
from app.chunking import chunk_all

client = chromadb.PersistentClient(path="data/chroma")  # saved on disk
COLLECTION = "curriculum_chunks"


def get_collection(name=COLLECTION):
    return client.get_or_create_collection(
        name=name,
        embedding_function=embed.embedder,
        metadata={"hnsw:space": "cosine"},
    )


def index_all(max_chars=1000, name=COLLECTION):
    # start fresh, so old chunks do not stay in the index
    try:
        client.delete_collection(name)
    except Exception:
        pass
    collection = get_collection(name)
    chunks = chunk_all(max_chars=max_chars)
    for start in range(0, len(chunks), 100):          # add 100 chunks at a time
        batch = chunks[start:start + 100]
        collection.upsert(
            ids=[c["id"] for c in batch],
            documents=[embed.chunk_to_text(c) for c in batch],
            metadatas=[{"source": c["source"], "page": c["page"], "title": c["title"]} for c in batch],
        )
        print("indexed", start + len(batch), "of", len(chunks))
    print("Collection", name, "now has", collection.count(), "chunks")


def query(text, k=5, name=COLLECTION, max_chars=300):
    collection = get_collection(name)
    result = collection.query(query_texts=[text], n_results=k)
    hits = []
    for i in range(len(result["ids"][0])):
        meta = result["metadatas"][0][i]
        chunk_text = result["documents"][0][i]
        if max_chars is not None:
            chunk_text = chunk_text[:max_chars]
        hits.append({
            "score": round(1 - result["distances"][0][i], 3),   # cosine distance -> similarity
            "source": meta["source"],
            "page": meta["page"],
            "title": meta["title"],
            "text": chunk_text,
        })
    return hits


if __name__ == "__main__":
    index_all()