
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

def is_summary_request(question):
    """Detect requests to summarize the story read so far."""
    if not question:
        return False
    
    summary_patterns = [
        r"\bsummary\b",
        r"\bsummarize\b",
        r"\bsummarise\b",
        r"\brecap\b",
        r"\bwhat happened (?:till|until|up to) now\b",
        r"\bwhat has happened so far\b",
        r"\bwhat happened so far\b",
        r"\bstory so far\b",
        r"\b(?:everything|all) (?:that has )?happened so far\b",
        r"\bcatch me up\b",
        r"\bup to this point\b",
    ]

    return any(
        re.search(pattern, question.lower())
        for pattern in summary_patterns
    )
    
def retrieve_summary_chunks(book_id, current_chapter):
    """
    Retrieve all chunks from chapters up to the reader's
    current chapter, ordered by chapter and chunk.
    """
    with get_db_connection() as connection:
        rows = connection.execute(
        """
        SELECT
        ch.chapter_number,
        ch.title AS chapter_title,
        c.chunk_number,
        c.text,
        1.0 AS similarity
        FROM chunks AS c
        JOIN chapters AS ch
        ON c.chapter_id = ch.id
        WHERE c.book_id = ?
        AND ch.book_id = ?
        AND ch.chapter_number <= ?
        ORDER BY ch.chapter_number, c.chunk_number
        """,
        (book_id, book_id, current_chapter),
        ).fetchall()
        
    return [dict(row) for row in rows if row["text"].strip()]