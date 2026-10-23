import sqlite3
from pathlib import Path

database_path = Path(__file__).resolve().parent / "instance" / "litlens.db"

def get_db_connection():
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
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
        
        connection.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                entity_name TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                FOREIGN KEY (book_id)
                    REFERENCES books (id)
                    ON DELETE CASCADE,
                UNIQUE (book_id, normalized_name, entity_type)
            )
        """)

       
        connection.execute("""
            CREATE TABLE IF NOT EXISTS entity_mentions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                chapter_id INTEGER NOT NULL,
                mention_text TEXT NOT NULL,
                start_char INTEGER NOT NULL,
                end_char INTEGER NOT NULL,
                FOREIGN KEY (entity_id)
                    REFERENCES entities (id)
                    ON DELETE CASCADE,
                FOREIGN KEY (chapter_id)
                    REFERENCES chapters (id)
                    ON DELETE CASCADE
            )
        """)

        
        # Improve lookup performance
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_entities_book
            ON entities (book_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_entity_mentions_chapter
            ON entity_mentions (chapter_id)
        """)




if __name__ == "__main__":
    init_db()
    print("database initiliazed ")