import chromadb
from app import embed
from app.chunking import chunk_all

client = chromadb.PersistentClient(path="data/chroma")  # saved on disk


def get_collection():
    return client.get_or_create_collection(
        name="curriculum_chunks",
        embedding_function=embed.embedder,
        metadata={"hnsw:space": "cosine"},
    )


def index_all():
    # start fresh, so chunks from an older version of the chunker do not stay in the index
    try:
        client.delete_collection("curriculum_chunks")
    except Exception:
        pass
    collection = get_collection()
    chunks = chunk_all()
    for start in range(0, len(chunks), 100):          # add 100 chunks at a time
        batch = chunks[start:start + 100]
        collection.upsert(
            ids=[c["id"] for c in batch],
            documents=[embed.chunk_to_text(c) for c in batch],
            metadatas=[{"source": c["source"], "page": c["page"], "title": c["title"]} for c in batch],
        )
        print("indexed", start + len(batch), "of", len(chunks))
    print("Collection now has", collection.count(), "chunks")


def query(text, k=5):
    collection = get_collection()
    result = collection.query(query_texts=[text], n_results=k)
    hits = []
    for i in range(len(result["ids"][0])):
        meta = result["metadatas"][0][i]
        hits.append({
            "score": round(1 - result["distances"][0][i], 3),   # cosine distance -> similarity
            "source": meta["source"],
            "page": meta["page"],
            "title": meta["title"],
            "text": result["documents"][0][i][:300],
        })
    return hits


if __name__ == "__main__":
    index_all()