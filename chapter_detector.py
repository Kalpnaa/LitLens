
import re


NUMBER_PATTERN = (
    r"(?:\d+|[IVXLCDM]+|"
    r"ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|"
    r"ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN|"
    r"SIXTEEN|SEVENTEEN|EIGHTEEN|NINETEEN|TWENTY)"
)

HEADING_PATTERN = re.compile(
    rf"^\s*(?P<type>CHAPTERS?|CHAP\.?|ACTS?|SCENES?|PARTS?|BOOKS?)"
    rf"\s+(?P<number>{NUMBER_PATTERN})"
    rf"(?:\s*[:.\-–—]\s*|\s+)?"
    rf"(?P<title>.*?)\s*$",
    re.IGNORECASE,
)

SPECIAL_HEADING_PATTERN = re.compile(
    r"^\s*(?P<title>PROLOGUE|EPILOGUE|"
    r"INTRODUCTION|FOREWORD|AFTERWORD)\s*$",
    re.IGNORECASE,
)


def detect_chapters(text):
    """Split book text into sequential sections using recognized headings."""

    sections = []
    current_title = "Beginning"
    current_type = "beginning"
    current_lines = []
    section_number = 0

    def save_section():
        content = "\n".join(current_lines).strip()

        if content:
            sections.append({
                "chapter_number": len(sections) + 1,
                "heading_type": current_type,
                "title": current_title,
                "text": content,
            })

    for line in text.splitlines():
        heading = HEADING_PATTERN.match(line)
        special = SPECIAL_HEADING_PATTERN.match(line)

        if heading or special:
            save_section()
            current_lines = []

            if heading:
                current_type = heading.group("type").upper().rstrip(".")
                number = heading.group("number")
                title = heading.group("title").strip(" :-–—.")
                current_title = f"{heading.group('type')} {number}"
                if title:
                    current_title += f": {title}"
            else:
                current_type = "section"
                current_title = special.group("title").title()

            section_number += 1
        else:
            current_lines.append(line)

    save_section()

    # If no heading was detected, keep the whole book as one section.
    if section_number == 0 and sections:
        sections[0]["chapter_number"] = 1

    return sections
