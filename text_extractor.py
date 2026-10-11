from pathlib import Path
import re
import fitz

def extract_text(file_path):
    """Extract readable text from a pdf or text file"""
    
    path = Path(file_path)
    file_type = path.suffix.lower()
    
    if not path.exists() or not path.is_file():
        raise FileNotFoundError("The book file was not found")
    
    if file_type == ".txt":
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            text = path.read_text(encoding="cp1252")
    
    elif file_type == ".pdf":
        try:
            with fitz.open(path) as document:
                if document.is_encrypted:
                    raise ValueError(
                        "Password-protected PDFs are not supported yet"
                    )
                    
                page_texts = [
                    page.get_text("text")
                    for page in document
                ]
                
                text = "\n\n".join(page_texts)
        
        except (fitz.FileDataError, RuntimeError) as error:
            raise ValueError(
                "The PDF could not be read. Check that it is a valid PDF."
            ) from error
    
    else:
        raise ValueError("Only PDF and TXT files are supported.")
    
    
    # Remove trailing spaces while preserving paragraph breaks.
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    
    if not text:
        raise ValueError(
            "No readable text was found. The file may be empty "
            "or the PDF may contain scanned pages."
        )

    return text


