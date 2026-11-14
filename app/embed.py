import numpy as np
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

# small free model (all-MiniLM-L6-v2). It is downloaded once on first use.
embedder = DefaultEmbeddingFunction()


def chunk_to_text(chunk):
    # the title is added so the course name helps the match
    return chunk["title"] + "\n" + chunk["text"]


def embed_texts(texts):
    return np.array(embedder(texts))


def semantic_search(chunks, vectors, query, k=3):
    q = np.array(embedder([query])[0])
    # cosine similarity = dot product divided by the lengths
    scores = vectors @ q / (np.linalg.norm(vectors, axis=1) * np.linalg.norm(q))
    best = scores.argsort()[::-1][:k]
    hits = []
    for i in best:
        hits.append({"score": round(float(scores[i]), 3), "chunk": chunks[i]})
    return hits