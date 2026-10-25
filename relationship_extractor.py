
import re
import spacy
from database import get_db_connection

# Use the large English model you installed.
try:
    nlp = spacy.load("en_core_web_lg")
except OSError as error:
    raise RuntimeError(
        "The spaCy English model is missing. "
        "Run: python -m spacy download en_core_web_lg"
    ) from error


# Patterns are applied to individual sentences.
# These are initial rules, not a complete relationship parser.
RELATIONSHIP_RULES = [
    
    # Character descriptions in cast lists, e.g. "Romeo, son to Montague."
    (
        "family",
        re.compile(
            r"\b(?P<first>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)"
            r"\s*,\s*(?:the\s+)?"
            r"(?P<relation>son|daughter|child|nephew|niece|"
            r"kinsman|kinswoman|wife|husband|father|mother|"
            r"brother|sister|cousin)\s+"
            r"(?:to|of)\s+"
            r"(?P<second>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)\b"
        ),
        "directed",
    ),

    # Friendship stated in a character description.
    # Example: "Mercutio, kinsman to the Prince and friend to Romeo."
    (
        "friendship",
        re.compile(
            r"\b(?P<first>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)"
            r"\s*,(?:(?![.!?]).)*?"
            r"\bfriend\s+(?:to|of|with)\s+"
            r"(?P<second>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)\b"
        ),
        "mutual",
    ),

    # Family relationships with explicit direction.
        
    (
        "family",
        re.compile(
            r"\b(?P<child>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)*)\s+"
            r"is\s+the\s+(?P<relation>son|daughter|child)\s+of\s+"
            r"(?P<parent>(?:Lord|Lady|Sir|Dame|Dr\.?)\s+)?"
            r"(?P<parent_name>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)*)",
            
        ),
        "child_to_parent",
    ),
    (
        "family",
        re.compile(
            r"\b(?P<parent>(?:Lord|Lady|Sir|Dame|Dr\.?)\s+)?"
            r"(?P<parent_name>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)*)\s+"
            r"is\s+the\s+(?P<relation>father|mother|parent)\s+of\s+"
            r"(?P<child>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)*)",
            
        ),
        "parent_to_child",
    ),


    # Explicit romantic relationships.
    (
        "romantic",
        re.compile(
            r"\b(?P<first>[A-Z][\w'-]*)\s+"
            r"(?:loves|loved|adores|adored)\s+"
            r"(?P<second>[A-Z][\w'-]*)\b",
            
        ),
        "directed",
    ),

    # Explicit conflict relationships.
    (
        "conflict",
        re.compile(
            r"\b(?P<first>[A-Z][\w'-]*)\s+"
            r"(?:is|was|remains)\s+"
            r"(?:an?\s+)?"
            r"(?:enemy|rival)\s+of\s+"
            r"(?P<second>[A-Z][\w'-]*)\b",
        ),
        "mutual",
    ),
    (
        "conflict",
        re.compile(
            r"\b(?P<first>[A-Z][\w'-]*)\s+"
            r"(?:hates|hated|fights|fought)\s+"
            r"(?P<second>[A-Z][\w'-]*)\b",
            
        ),
        "directed",
    ),
        # Romantic relationships expressed in different ways.
    (
        "romantic",
        re.compile(
            r"\b(?P<first>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)\s+"
            r"(?:is|was|falls|fell)\s+in love with\s+"
            r"(?P<second>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)\b"
        ),
        "directed",
    ),
    (
        "romantic",
        re.compile(
            r"\b(?P<first>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)\s+"
            r"(?:is|was)\s+fond of\s+"
            r"(?P<second>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)\b"
        ),
        "directed",
    ),

    # Friendship and trust.
    (
        "friendship",
        re.compile(
            r"\b(?P<first>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)\s+"
            r"(?:is|are|was|were|became)\s+friends?\s+with\s+"
            r"(?P<second>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)\b"
        ),
        "mutual",
    ),
    (
        "friendship",
        re.compile(
            r"\b(?P<first>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)\s+"
            r"(?:trusts|trusted|helps|helped|supports|supported)\s+"
            r"(?P<second>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)\b"
        ),
        "directed",
    ),

    # Arguments and fighting.
    (
        "conflict",
        re.compile(
            r"\b(?P<first>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)\s+"
            r"(?:argues|argued|fights|fought)\s+with\s+"
            r"(?P<second>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)\b"
        ),
        "mutual",
    ),

    # Sibling relationships.
    (
        "family",
        re.compile(
            r"\b(?P<first>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)\s+"
            r"is\s+the\s+(?:brother|sister|sibling)\s+of\s+"
            r"(?P<second>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)\b"
        ),
        "directed",
    ),
]


def clean_name(name):
    """Normalize whitespace and surrounding punctuation."""
    return re.sub(r"\s+", " ", name).strip(" ,.;:!?\"'")


def extract_relationships_from_text(text, chapter_number=None):
    """
    Extract candidate relationships from explicit sentence patterns.

    Returns character names, relationship category, direction,
    chapter number, and the supporting sentence.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    results = []
    seen = set()
    doc = nlp(text)

    for sentence in doc.sents:
        sentence_text = sentence.text.strip()

        for category, pattern, direction in RELATIONSHIP_RULES:
            for match in pattern.finditer(sentence_text):
                groups = match.groupdict()

                
                if direction == "child_to_parent":
                    source = groups["child"]
                    title = groups.get("parent") or ""
                    parent_name = groups["parent_name"]
                    target = f"{title} {parent_name}".strip()
                    relation = groups["relation"].casefold()

                elif direction == "parent_to_child":
                    title = groups.get("parent") or ""
                    parent_name = groups["parent_name"]
                    source = f"{title} {parent_name}".strip()
                    target = groups["child"]
                    relation = groups["relation"].casefold()


                else:
                    source = groups["first"]
                    target = groups["second"]
                    relation = category

                source = clean_name(source)
                target = clean_name(target)

                if not source or not target:
                    continue

                if source.casefold() == target.casefold():
                    continue

                key = (
                    source.casefold(),
                    target.casefold(),
                    category,
                    chapter_number,
                    sentence_text.casefold(),
                )

                if key in seen:
                    continue

                seen.add(key)

                results.append({
                    "source_character": source,
                    "target_character": target,
                    "relationship_type": category,
                    "relationship_detail": relation,
                    "direction": direction,
                    "chapter_number": chapter_number,
                    "evidence": sentence_text,
                })

    return results


def normalize_name(name):
    """Normalize a character name for database matching."""
    return re.sub(r"\s+", " ", name).strip().casefold()


def get_known_character_names(book_id):
    """Return existing character names for a book."""
    connection = get_db_connection()

    try:
        rows = connection.execute(
            """
            SELECT entity_name, normalized_name
            FROM entities
            WHERE book_id = ?
              AND entity_type = 'PERSON'
            """,
            (book_id,),
        ).fetchall()

        return {
            row["normalized_name"]: row["entity_name"]
            for row in rows
        }

    finally:
        connection.close()

def filter_relationships_by_known_characters(book_id, relationships):
    """Keep relationships whose endpoints match known character entities."""
    known_names = get_known_character_names(book_id)
    filtered = []

    for relationship in relationships:
        source = normalize_name(relationship["source_character"])
        target = normalize_name(relationship["target_character"])

        source_id_name = source if source in known_names else None
        target_id_name = target if target in known_names else None

        # Support titles such as "Lord Capulet" when "Capulet"
        # is the existing character entity.
        if source_id_name is None:
            source = re.sub(
                r"^(lord|lady|sir|dame|dr\.?)\s+",
                "",
                source,
                flags=re.IGNORECASE,
            )
            source_id_name = source if source in known_names else None

        if target_id_name is None:
            target = re.sub(
                r"^(lord|lady|sir|dame|dr\.?)\s+",
                "",
                target,
                flags=re.IGNORECASE,
            )
            target_id_name = target if target in known_names else None

        if source_id_name and target_id_name:
            filtered.append(relationship)

    return filtered


def find_entity_id(cursor, book_id, character_name):
    """Match an extracted name to an existing entity."""
    normalized = normalize_name(character_name)

    # First try an exact match.
    row = cursor.execute(
        """
        SELECT id FROM entities
        WHERE book_id = ? AND normalized_name = ?
        ORDER BY CASE WHEN entity_type = 'PERSON' THEN 0 ELSE 1 END
        LIMIT 1
        """,
        (book_id, normalized),
    ).fetchone()

    if row:
        return row["id"]

    # If a title is present, try matching the name without that title.
    without_title = re.sub(
        r"^(lord|lady|sir|dame|dr\.?)\s+",
        "",
        character_name.strip(),
        flags=re.IGNORECASE,
    )
    normalized_without_title = normalize_name(without_title)

    if normalized_without_title != normalized:
        row = cursor.execute(
            """
            SELECT id FROM entities
            WHERE book_id = ? AND normalized_name = ?
            ORDER BY CASE WHEN entity_type = 'PERSON' THEN 0 ELSE 1 END
            LIMIT 1
            """,
            (book_id, normalized_without_title),
        ).fetchone()

        if row:
            return row["id"]

    return None


def store_relationships(book_id, relationships):
    """
    Store relationships only when both characters already exist
    in the book's Phase 7 entity records.
    """
    connection = get_db_connection()
    stored_count = 0
    skipped_count = 0

    try:
        cursor = connection.cursor()

        for relationship in relationships:
            source_name = normalize_name(
                relationship["source_character"]
            )
            target_name = normalize_name(
                relationship["target_character"]
            )
            chapter_number = relationship.get("chapter_number")

            if not chapter_number:
                skipped_count += 1
                continue

            
            source_id = find_entity_id(
                cursor, book_id, relationship["source_character"]
            )

            target_id = find_entity_id(
                cursor, book_id, relationship["target_character"]
            )

            
            chapter_id = relationship.get("chapter_id")

            if chapter_id is not None:
                chapter = cursor.execute(
                    """
                    SELECT id FROM chapters
                    WHERE id = ? AND book_id = ?
                    LIMIT 1
                    """,
                    (chapter_id, book_id),
                ).fetchone()
            else:
                chapter = cursor.execute(
                    """
                    SELECT id FROM chapters
                    WHERE book_id = ? AND chapter_number = ?
                    LIMIT 1
                    """,
                    (book_id, chapter_number),
                ).fetchone()

            # Do not create new characters or guess missing chapters.
            if source_id is None or target_id is None or chapter is None:
                skipped_count += 1
                continue

            values = (
                book_id,
                source_id,
                target_id,
                relationship["relationship_type"],
                relationship.get("relationship_detail"),
                relationship["direction"],
                chapter["id"],
                relationship["evidence"],
            )

            existing = cursor.execute(
                """
                SELECT id FROM character_relationships
                WHERE book_id = ?
                  AND source_entity_id = ?
                  AND target_entity_id = ?
                  AND relationship_type = ?
                  AND chapter_id = ?
                  AND evidence = ?
                LIMIT 1
                """,
                (
                    book_id,
                    source_id,
                    target_id,
                    relationship["relationship_type"],
                    chapter["id"],
                    relationship["evidence"],
                ),
            ).fetchone()

            if existing:
                continue

            cursor.execute(
                """
                INSERT INTO character_relationships (
                    book_id,
                    source_entity_id,
                    target_entity_id,
                    relationship_type,
                    relationship_detail,
                    direction,
                    chapter_id,
                    evidence
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )
            stored_count += 1

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return {
        "stored": stored_count,
        "skipped": skipped_count,
    }


def get_character_relationships(book_id, current_chapter):
    """
    Return stored relationships revealed by the current chapter.
    Future-chapter relationships are excluded.
    """
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        rows = cursor.execute(
            """
            SELECT
                source.entity_name AS source_character,
                target.entity_name AS target_character,
                r.relationship_type,
                r.relationship_detail,
                r.direction,
                c.chapter_number,
                r.evidence
            FROM character_relationships AS r
            JOIN entities AS source
                ON source.id = r.source_entity_id
            JOIN entities AS target
                ON target.id = r.target_entity_id
            JOIN chapters AS c
                ON c.id = r.chapter_id
            WHERE r.book_id = ?
              AND c.chapter_number <= ?
            ORDER BY c.chapter_number ASC, r.id ASC
            """,
            (book_id, current_chapter),
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


if __name__ == "__main__":
    tests = [
    "Alice is in love with Daniel.",
    "Maya is friends with Priya.",
    "Arjun trusts Rohan.",
    "Olivia argued with Ethan.",
    "Sofia is the sister of Lucas.",
    "The weather is beautiful today.",
]

    for sentence in tests:
        print(f"\nSentence: {sentence}")
        for result in extract_relationships_from_text(sentence, 1):
            print(result)
