from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def record_text(record):
    # the text we search in: code + title + category
    category = record["l_t_p_credits"]["category"]
    return record["course_code"] + " " + record["course_title"] + " " + category


def smart_search(records, query, top_k=5):
    texts = [record_text(r) for r in records]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)       # TF-IDF of every record
    query_vector = vectorizer.transform([query])   # TF-IDF of the query
    scores = cosine_similarity(query_vector, matrix)[0]

    ranked = sorted(range(len(records)), key=lambda i: scores[i], reverse=True)
    results = []
    for i in ranked[:top_k]:
        if scores[i] > 0:
            results.append({"score": round(float(scores[i]), 3), "record": records[i]})
    return results