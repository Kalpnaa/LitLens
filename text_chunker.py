
import re


def chunk_text(text, max_words=180, overlap_sentences=1):
    """
    Split section text into smaller chunks.

    max_words: approximate maximum words per chunk.
    overlap_sentences: number of ending sentences reused
                       at the beginning of the next chunk.
    """

    if not text or not text.strip():
        return []

    if max_words < 1:
        raise ValueError("max_words must be at least 1.")

    if overlap_sentences < 0:
        raise ValueError("overlap_sentences cannot be negative.")

    # Normalize whitespace while retaining readable sentence text.
    text = re.sub(r"\s+", " ", text).strip()

    # Basic sentence splitting; more advanced NLP can improve this later.
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Split unusually long sentences so chunks stay manageable.
    pieces = []

    for sentence in sentences:
        words = sentence.split()

        for start in range(0, len(words), max_words):
            pieces.append(" ".join(words[start:start + max_words]))

    chunks = []
    current = []
    current_words = 0

    for piece in pieces:
        piece_words = len(piece.split())

        if current and current_words + piece_words > max_words:
            chunks.append(" ".join(current))

            # Reuse a small amount of context from the previous chunk.
            current = current[-overlap_sentences:] if overlap_sentences else []
            current_words = sum(len(item.split()) for item in current)

            # Avoid an oversized chunk when the overlap itself is too large.
            while current and current_words + piece_words > max_words:
                removed = current.pop(0)
                current_words -= len(removed.split())

        current.append(piece)
        current_words += piece_words

    if current:
        chunks.append(" ".join(current))

    return [
        {
            "chunk_number": index + 1,
            "text": chunk,
            "word_count": len(chunk.split()),
        }
        for index, chunk in enumerate(chunks)
    ]
