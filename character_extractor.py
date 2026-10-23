
import re
import spacy

from database import get_db_connection


# Load the English NLP model once when the module is imported.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError as error:
    raise RuntimeError(
        "The spaCy English model is missing. "
        "Run: python -m spacy download en_core_web_sm"
    ) from error


# Entity types relevant to LitLens.
SUPPORTED_ENTITY_TYPES = {
    "PERSON",
    "GPE",
    "LOC",
    "ORG",
    "FAC",
}


def normalize_entity_name(name):
    """
    Normalize an entity name for consistent database storage.

    Example:
        ' Romeo ' -> 'romeo'
    """
    name = re.sub(r"\s+", " ", name).strip()
    return name.casefold()


def extract_entities_from_text(text):
    """
    Extract named entities from one chapter.

    Returns a list of entities with their types and character
    positions in the original chapter text.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    doc = nlp(text)

    extracted = []

    for entity in doc.ents:
        if entity.label_ not in SUPPORTED_ENTITY_TYPES:
            continue

        entity_name = re.sub(r"\s+", " ", entity.text).strip()
        normalized_name = normalize_entity_name(entity_name)

        if not normalized_name:
            continue

        extracted.append({
            "entity_name": entity_name,
            "normalized_name": normalized_name,
            "entity_type": entity.label_,
            "start_char": entity.start_char,
            "end_char": entity.end_char,
        })

    return extracted


def extract_and_store_book_entities(book_id):
    """
    Extract and store entities from every processed chapter
    belonging to a book.

    Existing entity data for this book is replaced so that
    repeated processing does not create duplicate mentions.
    """
    with get_db_connection() as connection:

        book = connection.execute(
            "SELECT id FROM books WHERE id = ?",
            (book_id,),
        ).fetchone()

        if book is None:
            raise ValueError("Book not found.")

        chapters = connection.execute(
            """
            SELECT id, chapter_number, title, text
            FROM chapters
            WHERE book_id = ?
            ORDER BY chapter_number
            """,
            (book_id,),
        ).fetchall()

        if not chapters:
            raise ValueError(
                "No processed chapters found. Process the book first."
            )

        # Remove old mentions before old entities.
        # Foreign-key cascading also protects related records.
        connection.execute(
            """
            DELETE FROM entity_mentions
            WHERE entity_id IN (
                SELECT id FROM entities WHERE book_id = ?
            )
            """,
            (book_id,),
        )

        connection.execute(
            "DELETE FROM entities WHERE book_id = ?",
            (book_id,),
        )

        entity_cache = {}
        total_mentions = 0

        for chapter in chapters:
            text = chapter["text"] or ""

            # Process long chapters in manageable pieces.
            # Offsets are adjusted back to chapter-level positions.
            # spaCy's maximum document length is respected.
            step_size = 80000

            for offset in range(0, len(text), step_size):
                segment = text[offset:offset + step_size]
                extracted_entities = extract_entities_from_text(segment)

                for item in extracted_entities:
                    key = (
                        item["normalized_name"],
                        item["entity_type"],
                    )

                    if key not in entity_cache:
                        cursor = connection.execute(
                            """
                            INSERT INTO entities (
                                book_id,
                                entity_name,
                                normalized_name,
                                entity_type
                            )
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                book_id,
                                item["entity_name"],
                                item["normalized_name"],
                                item["entity_type"],
                            ),
                        )

                        entity_cache[key] = cursor.lastrowid

                    entity_id = entity_cache[key]

                    connection.execute(
                        """
                        INSERT INTO entity_mentions (
                            entity_id,
                            chapter_id,
                            mention_text,
                            start_char,
                            end_char
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            entity_id,
                            chapter["id"],
                            item["entity_name"],
                            item["start_char"] + offset,
                            item["end_char"] + offset,
                        ),
                    )

                    total_mentions += 1

    return {
        "chapters": len(chapters),
        "entities": len(entity_cache),
        "mentions": total_mentions,
    }


if __name__ == "__main__":
    print("LitLens character extraction module loaded successfully.")
