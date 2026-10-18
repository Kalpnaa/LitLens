import sqlite3
from pathlib import Path

database_path = Path(__file__).resolve().parent / "instance" / "litlens.db"

def get_db_connection():
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    database_path.parent.mkdir(parents=True,exist_ok=True)
    
    with get_db_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS books(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL UNIQUE,
                file_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                processing_status TEXT NOT NULL DEFAULT 'pending'
                )
                """)
        
        connection.execute("""
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                chapter_number INTEGER NOT NULL,
                heading_type TEXT NOT NULL,
                title TEXT NOT NULL,
                text TEXT NOT NULL,
                FOREIGN KEY (book_id)
                    REFERENCES books (id)
                    ON DELETE CASCADE,
                UNIQUE (book_id, chapter_number)
            )
        """)
        
        
        connection.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                chapter_id INTEGER NOT NULL,
                chunk_number INTEGER NOT NULL,
                text TEXT NOT NULL,
                word_count INTEGER NOT NULL,
                FOREIGN KEY (book_id)
                    REFERENCES books (id)
                    ON DELETE CASCADE,
                FOREIGN KEY (chapter_id)
                    REFERENCES chapters (id)
                    ON DELETE CASCADE,
                UNIQUE (chapter_id, chunk_number)
            )
        """)



if __name__ == "__main__":
    init_db()
    print("database initiliazed ")