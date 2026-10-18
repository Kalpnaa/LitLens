from database import get_db_connection
from text_chunker import chunk_text

def process_chunks(book_id, max_words=180, overlap_sentences=1):
    """Create and store chunks for all saved sections of a book."""
    
    with get_db_connection() as connection:
        book = connection.execute(
            "SELECT id FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()
        
        if book is None:
            raise ValueError("book not found.")
        
        sections = connection.execute(
            """
            SELECT id,text
            FROM chapters
            WHERE book_id = ?
            ORDER BY chapter_number
            """,
            (book_id,)
        ).fetchall()
        
        if not sections:
            raise ValueError(
                "No processed sections found.process the book"
            )
            
        rows = []
        
        for section in sections:
            chunks = chunk_text(
                section["text"],
                max_words = max_words,
                overlap_sentences = overlap_sentences,
            )
            
            for chunk in chunks:
                rows.append((
                    book_id,
                    section["id"],
                    chunk["chunk_number"],
                    chunk["text"],
                    chunk["word_count"],
                ))
        if not rows:
            raise ValueError("no text chunks could be generated.")
        
        connection.execute(
            "DELETE FROM chunks WHERE book_id = ?",
            (book_id,)
        )
        
        connection.executemany(
            """
            INSERT INTO chunks(
                book_id, chapter_id, chunk_number, text, word_count
            )
            VALUES(?,?,?,?,?)
            """,
            rows,
        )
        
    return len(rows)
