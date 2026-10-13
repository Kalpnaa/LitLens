from pathlib import Path
from database import get_db_connection
from text_extractor import extract_text
from chapter_detector import detect_chapters

def process_book(book_id):
    """Extract,detect and save sections for an uploaded book."""
    with get_db_connection() as connection:
        book = connection.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()
        
    if book is None:
        raise ValueError("Book not found in database")
    
    file_path = Path(book["file_path"])

    if not file_path.is_file():
        raise FileNotFoundError("the uploaded book file is not found")
    
    text = extract_text(file_path)
    sections = detect_chapters(text)
    
    if not sections:
        raise ValueError("sections are not readable and detected")
    
    with get_db_connection() as connection:
        connection.execute(
            "DELETE FROM CHAPTERS WHERE book_id = ?",
            (book_id,)
        )
        
        connection.executemany(
            """
            INSERT INTO CHAPTERS(
                book_id,chapter_number,heading_type,title,text)
                VALUES(?,?,?,?,?)""",
                  [
                (
                    book_id,
                    section["chapter_number"],
                    section["heading_type"],
                    section["title"],
                    section["text"],
                )
                for section in sections
            ],
            
        )
        connection.execute(
            """
            UPDATE books
            SET processing_status = ?
            WHERE id = ?
            """,
            ("completed", book_id)
        )
         
        return len(sections)