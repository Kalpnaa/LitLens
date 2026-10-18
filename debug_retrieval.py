
from database import get_db_connection

with get_db_connection() as connection:
    print("\n--- FIRST 5 SECTIONS ---")

    sections = connection.execute(
        """
        SELECT chapter_number, heading_type, title, text
        FROM chapters
        WHERE book_id = 2
        ORDER BY chapter_number
        LIMIT 5
        """
    ).fetchall()

    for section in sections:
        print(f"\nSection {section['chapter_number']}: "
              f"{section['title']}")
        print(section["text"][:500])

    print("\n--- KEYWORD MATCHES ACROSS ALL SECTIONS ---")

    matches = connection.execute(
        """
        SELECT ch.chapter_number, ch.title, c.chunk_number, c.text
        FROM chunks AS c
        JOIN chapters AS ch ON ch.id = c.chapter_id
        WHERE c.book_id = 2
          AND (
              LOWER(c.text) LIKE '%montague%'
              OR LOWER(c.text) LIKE '%capulet%'
              OR LOWER(c.text) LIKE '%verona%'
              OR LOWER(c.text) LIKE '%grudge%'
          )
        ORDER BY ch.chapter_number, c.chunk_number
        LIMIT 10
        """
    ).fetchall()

    for match in matches:
        print(
            f"\nSection {match['chapter_number']}: "
            f"{match['title']} | Chunk {match['chunk_number']}"
        )
        print(match["text"][:400])

    if not matches:
        print("No matching keywords found in any stored chunk.")
