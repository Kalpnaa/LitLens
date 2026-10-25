
from pathlib import Path

from database import get_db_connection
from text_extractor import extract_text
from chapter_detector import detect_chapters
from text_chunker import chunk_text
from character_extractor import extract_and_store_book_entities
from relationship_extractor import extract_relationships_from_text,store_relationships,filter_relationships_by_known_characters

def process_book(book_id, max_words=180, overlap_sentences=1):
    """Extract, detect, save sections, and create searchable chunks."""

    with get_db_connection() as connection:
        book = connection.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

        if book is None:
            raise ValueError("Book not found in the database.")

        file_path = Path(book["file_path"])

        if not file_path.is_file():
            raise FileNotFoundError("The uploaded book file is missing.")

        text = extract_text(file_path)
        sections = detect_chapters(text)

        if not sections:
            raise ValueError("No readable sections were detected.")

        # Prepare sections and their chunks before changing saved records.
        prepared_sections = []

        for section in sections:
            chunks = chunk_text(
                section["text"],
                max_words=max_words,
                overlap_sentences=overlap_sentences,
            )

            prepared_sections.append((section, chunks))

        if not any(chunks for _, chunks in prepared_sections):
            raise ValueError("No text chunks could be generated.")

        # Replace old chunks and sections atomically.
        connection.execute(
        "DELETE FROM character_relationships WHERE book_id = ?",
        (book_id,)
        )
        connection.execute(
            "DELETE FROM chunks WHERE book_id = ?",
            (book_id,)
        )
        connection.execute(
            "DELETE FROM chapters WHERE book_id = ?",
            (book_id,)
        )

        total_chunks = 0

        for section, chunks in prepared_sections:
            cursor = connection.execute(
                """
                INSERT INTO chapters (
                    book_id, chapter_number, heading_type, title, text
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    book_id,
                    section["chapter_number"],
                    section["heading_type"],
                    section["title"],
                    section["text"],
                ),
            )

            chapter_id = cursor.lastrowid

            connection.executemany(
                """
                INSERT INTO chunks (
                    book_id, chapter_id, chunk_number, text, word_count
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        book_id,
                        chapter_id,
                        chunk["chunk_number"],
                        chunk["text"],
                        chunk["word_count"],
                    )
                    for chunk in chunks
                ],
            )

            total_chunks += len(chunks)

        connection.execute(
            """
            UPDATE books
            SET processing_status = ?
            WHERE id = ?
            """,
            ("completed", book_id),
        )
    
    entity_results = extract_and_store_book_entities(book_id)
    all_relationships = []

    with get_db_connection() as connection:
        chapters = connection.execute(
            """
            SELECT id, chapter_number, text
            FROM chapters
            WHERE book_id = ?
            ORDER BY chapter_number
            """,
            (book_id,),
        ).fetchall()

    for chapter in chapters:
        relationships = extract_relationships_from_text(
            chapter["text"],
            chapter_number=chapter["chapter_number"],
        )

        # Keep the database chapter ID with each relationship.
        for relationship in relationships:
            relationship["chapter_id"] = chapter["id"]

        all_relationships.extend(relationships)

    all_relationships = filter_relationships_by_known_characters(
    book_id,
    all_relationships,
)
    relationship_results = store_relationships(
        book_id,
        all_relationships,
    )

    return {
        "sections": len(sections),
        "chunks": total_chunks,
        "entities": entity_results["entities"],
        "mentions": entity_results["mentions"],
        "relationships_detected": len(all_relationships),
        "relationships_stored": relationship_results["stored"],
        "relationships_skipped": relationship_results["skipped"],
    }
