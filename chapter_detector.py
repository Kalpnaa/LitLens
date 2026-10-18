
import re
from collections import Counter


NUMBER_PATTERN = (
    r"(?:\d+(?:\.\d+)*|[IVXLCDM]+|"
    r"ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|"
    r"ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN|"
    r"SIXTEEN|SEVENTEEN|EIGHTEEN|NINETEEN|TWENTY)"
)

HEADING_PATTERN = re.compile(
    rf"^\s*(?P<type>"
    r"CHAPTERS?|CHAP\.?|ACTS?|SCENES?|PARTS?|BOOKS?|"
    r"UNITS?|LESSONS?|SECTIONS?|LECTURES?|"
    r"VOLUMES?|MODULES?|PROLOGUES?|EPILOGUES?"
    rf")\s+(?P<number>{NUMBER_PATTERN})"
    r"(?:\s*[:.\-–—]\s*|\s+)?"
    r"(?P<title>.*?)\s*$",
    re.IGNORECASE,
)

SPECIAL_HEADING_PATTERN = re.compile(
    r"^\s*(?:THE\s+)?"
    r"(PROLOGUE|EPILOGUE|INTRODUCTION|FOREWORD|"
    r"PREFACE|AFTERWORD|CONCLUSION|ACKNOWLEDGEMENTS?|"
    r"ACKNOWLEDGMENTS?|DRAMATIS PERSONAE)"
    r"\s*$",
    re.IGNORECASE,
)

CONTENTS_PATTERN = re.compile(
    r"^\s*(?:TABLE\s+OF\s+)?CONTENTS\s*$",
    re.IGNORECASE,
)


def normalize_line(line):
    """Normalize a line for comparison."""
    return re.sub(r"\s+", " ", line).strip().casefold()


def find_body_start(lines):
    """
    Skip a table of contents when a repeated line helps identify
    where the actual book begins.

    If the structure is unclear, keep the original text rather
    than removing potentially useful content.
    """
    contents_index = next(
        (
            i for i, line in enumerate(lines)
            if CONTENTS_PATTERN.match(line)
        ),
        None,
    )

    if contents_index is None:
        return 0

    after_contents = [
        normalize_line(line)
        for line in lines[contents_index + 1:]
        if normalize_line(line)
    ]

    counts = Counter(after_contents)

    # The first repeated non-empty line after the contents marker
    # often marks the beginning of the actual text.
    for i in range(contents_index + 1, len(lines)):
        normalized = normalize_line(lines[i])

        if normalized and counts[normalized] > 1:
            later_match = next(
                (
                    j for j in range(i + 1, len(lines))
                    if normalize_line(lines[j]) == normalized
                ),
                None,
            )

            if later_match is not None:
                return later_match

    # Do not discard content if the boundary cannot be identified.
    return 0


def detect_chapters(text):
    """
    Detect sequential reading sections across common book formats.

    The returned chapter_number represents reading order, not
    necessarily the book's printed chapter or scene number.
    """
    lines = text.splitlines()

    body_start = find_body_start(lines)
    lines = lines[body_start:]

    sections = []
    current_title = "Beginning"
    current_type = "beginning"
    current_lines = []

    def save_section():
        content = "\n".join(current_lines).strip()

        if content:
            sections.append({
                "chapter_number": len(sections) + 1,
                "heading_type": current_type,
                "title": current_title,
                "text": content,
            })

    for line in lines:
        heading = HEADING_PATTERN.match(line)
        special = SPECIAL_HEADING_PATTERN.match(line)

        if heading or special:
            save_section()
            current_lines = []

            if heading:
                heading_type = heading.group("type").upper().rstrip(".")
                number = heading.group("number")
                title = heading.group("title").strip(" :-–—.")

                current_type = heading_type.lower()
                current_title = f"{heading_type.title()} {number}"

                if title:
                    current_title += f": {title}"

            else:
                current_type = "section"
                current_title = special.group(1).title()

        else:
            current_lines.append(line)

    save_section()

    # Fallback: if no usable headings were found, keep the book
    # as one section instead of losing its text.
    if not sections and text.strip():
        sections.append({
            "chapter_number": 1,
            "heading_type": "book",
            "title": "Full Book",
            "text": text.strip(),
        })

    return sections
