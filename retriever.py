
import re
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from database import get_db_connection


def preprocess_question(question):
    """Normalize a question before retrieval."""
    if not question or not question.strip():
        return ""

    question = question.lower()
    question = re.sub(r"[^\w\s]", " ", question)
    question = re.sub(r"\s+", " ", question).strip()

    return question



def retrieve_chunks(book_id, question, current_chapter, top_k=5):
    """Retrieve relevant chunks without exposing unread sections."""

    if not isinstance(question, str) or not question.strip():
        return []

    if (
        isinstance(current_chapter, bool)
        or not isinstance(current_chapter, int)
        or current_chapter < 1
    ):
        return []

    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
        return []

    question = re.sub(r"\s+", " ", question).strip()

    conn = get_db_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                c.id AS chunk_id,
                c.chapter_id,
                ch.chapter_number,
                ch.title AS chapter_title,
                c.chunk_number,
                c.text,
                c.word_count
            FROM chunks AS c
            JOIN chapters AS ch ON c.chapter_id = ch.id
            WHERE ch.book_id = ?
              AND ch.chapter_number <= ?
            ORDER BY ch.chapter_number, c.chunk_number
            """,
            (book_id, current_chapter),
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return []

    # Remove empty text before fitting TF-IDF.
    valid_rows = [
        row for row in rows
        if row["text"] and row["text"].strip()
    ]

    if not valid_rows:
        return []

    texts = [row["text"] for row in valid_rows]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english"
    )

    try:
        document_vectors = vectorizer.fit_transform(texts)
        question_vector = vectorizer.transform([question])
    except ValueError:
        # For example, no usable words in the question or documents.
        return []

    scores = cosine_similarity(
        question_vector, document_vectors
    ).flatten()

    results = []

    for index, score in enumerate(scores):
        # Exact zero means there is no shared TF-IDF vocabulary.
        if score <= 0:
            continue

        row = valid_rows[index]

        results.append({
            "chunk_id": row["chunk_id"],
            "chapter_id": row["chapter_id"],
            "chapter_number": row["chapter_number"],
            "chapter_title": row["chapter_title"],
            "chunk_number": row["chunk_number"],
            "text": row["text"],
            "word_count": row["word_count"],
            "similarity": float(score),
        })

    results.sort(key=lambda item: item["similarity"], reverse=True)

    return results[:top_k]