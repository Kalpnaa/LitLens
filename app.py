from flask import Flask,render_template,request,redirect,url_for
from werkzeug.utils import secure_filename
import os
import uuid
from pathlib import Path
import sqlite3
import uuid
from database import init_db,get_db_connection
from book_processor import process_book
from retriever import retrieve_chunks,retrieve_summary_chunks,is_summary_request
from llm import generate_answer
from relationship_extractor import get_character_relationships

app = Flask(__name__)

#store uploaded books
uploaded_folder = Path(app.instance_path) /"uploads"
uploaded_folder.mkdir(parents=True,exist_ok=True)



app.config["uploaded_folder"] = str(uploaded_folder)
app.config["max_content_length"] = 1024 * 1024 * 200  #200Mb file
Allowed_extension = {"pdf","txt"}


init_db()

def allowed_file(filename):
    return(
        "." in filename
        and filename.split(".",1)[1].lower() in Allowed_extension
    )
    
@app.route("/")
def home():
    return """<h1>hello litlens<h1>
               <p>your spolier-aware companion</p>
               <a href="/upload">Upload a book</a>
               <a href="/library">My Library </a>"""

@app.route("/upload", methods=["GET", "POST"])
def upload_book():
    if request.method == "POST":
        # 1. Check whether a file was submitted.
        if "book" not in request.files:
            return render_template(
                "upload.html", error="No file was submitted."
            )

        file = request.files["book"]

        # 2. Check whether the user selected a file.
        if file.filename == "":
            return render_template(
                "upload.html", error="Please select a book."
            )
         # 3. Validate the extension.
        if not allowed_file(file.filename):
            return render_template(
                "upload.html",
                error="Only PDF and TXT files are supported."
            )

        # 4. Create a safe, unique filename.
        original_name = secure_filename(file.filename)

        if not original_name:
            return render_template(
                "upload.html", error="Invalid filename."
            )

        extension = original_name.rsplit(".", 1)[1].lower()
        stored_name = f"{uuid.uuid4().hex}.{extension}"

        # 5. Save the actual file to disk.
        file_path = uploaded_folder / stored_name
        try:
            file.save(str(file_path))

            # Temporary confirmation; database registration comes next.
            with get_db_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO books (
                        title,
                        original_filename,
                        stored_filename,
                        file_type,
                        file_path
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        Path(original_name).stem,
                        original_name,
                        stored_name,
                        extension,
                        str(file_path.resolve()),
                    ),
                )

        except sqlite3.Error:
            # Avoid leaving an uploaded file without a database record.
            file_path.unlink(missing_ok=True)

            app.logger.exception("Failed to register uploaded book")

            return render_template(
                "upload.html",
                error="Could not register the book. Please try again."
            ), 500

        except OSError:
            app.logger.exception("Failed to save uploaded book")

            # The file may have been partially written.
            file_path.unlink(missing_ok=True)

            return render_template(
                "upload.html",
                error="Could not save the uploaded file."
            ), 500

        return redirect(url_for("library"))

    return render_template("upload.html")
  
  
@app.route("/library")
def library():
    with get_db_connection() as connection:
        books = connection.execute("""
            SELECT
                b.id,
                b.title,
                b.original_filename,
                b.file_type,
                b.uploaded_at,
                b.processing_status,
                COUNT(c.id) AS section_count
            FROM books AS b
            LEFT JOIN chapters AS c ON c.book_id = b.id
            GROUP BY b.id
            ORDER BY b.id DESC
        """).fetchall()

    return render_template(
        "library.html",
        books=books,
        message=request.args.get("message"),
        error=request.args.get("error")
    )
    
  
@app.errorhandler(413)
def file_too_large(error):
    return render_template(
        "upload.html",
        error="File is too large. The maximum size is 20 MB."
    ), 413  

@app.route("/proces/<int:book_id>",methods=["POST"])
def process_uploaded_book(book_id):
    try:
        result = process_book(book_id)

        message = (
            f"Book processed successfully: "
            f"{result['sections']} sections and "
            f"{result['chunks']} chunks saved."
        )

        
        return redirect(
            url_for("library",message=message)
        )
    
    except (ValueError, FileNotFoundError, OSError) as error:
        app.logger.warning("Book processing failed: %s", error)
        return redirect(url_for("library", error=str(error)))

    except Exception:
        app.logger.exception("Unexpected error while processing book")
        return redirect(
            url_for(
                "library",
                error="An unexpected error occurred during processing."
            )
        )

@app.route("/book/<int:book_id>",methods=["GET","POST"])
def read_book(book_id):
    answer = None
    sources = []
    question = ""
    current_chapter = 1
    error = None
    
    with get_db_connection() as connection:
        book = connection.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()
        
        if book is None:
            return redirect(
                url_for("library",error="book not found")
            )
        chapters = connection.execute(
            """
            SELECT chapter_number,title
            FROM chapters
            WHERE book_id = ?
            order by chapter_number
            """,
            (book_id,)
            
        ).fetchall()
    
    if book["processing_status"]!= "completed" or not chapters:
        return redirect(
            url_for(
                "library",
                error="please process this book before reading"
            )
        )
    
    if request.method == "POST":
        question = request.form.get("question","").strip()
        chapter_input = request.form.get("current_chapter","")
        
        try:
            current_chapter = int(chapter_input)
        except (TypeError,ValueError):
            error = "please select a valid chapter."
        
        valid_chapters = {
            chapter["chapter_number"] for chapter in chapters
        }
        if not error and current_chapter not in valid_chapters:
            error = "The selected chapter is not avaible"
            
        if not error and not question:
            error = "please enter a question or summary request"
            
        if not error:
            try:
                if is_summary_request(question):
                    results = retrieve_summary_chunks(
                        book_id = book_id,
                        current_chapter=current_chapter
                    )
                else:
                    results= retrieve_chunks(
                        book_id=book_id,
                        question=question,
                        current_chapter=current_chapter,
                        top_k=5
                    )
                    
                                
                if not results:
                    error = (
                        "I couldn't find relevant information "
                        "in the chapters you've read so far."
                    )
                else:
                    # Build context from the retrieved book passages.
                    context = "\n\n".join(
                        (
                            f"Chapter {item['chapter_number']}: "
                            f"{item['chapter_title']}\n"
                            f"{item['text']}"
                        )
                        for item in results
                    )

                    # Retrieve relationships only up to the current chapter.
                    relationships = get_character_relationships(
                        book_id,
                        current_chapter
                    )

                    # Format stored relationships for the LLM.
                    if relationships:
                        relationship_context = "\n".join(
                            (
                                f"- {item['source_character']} -> "
                                f"{item['relationship_type']} -> "
                                f"{item['target_character']}. "
                                f"Details: {item['relationship_detail']}. "
                                f"Evidence: {item['evidence']}"
                            )
                            for item in relationships
                        )

                        context += (
                            "\n\nCharacter relationship information "
                            "from chapters read so far:\n"
                            + relationship_context
                        )

                    # Generate an answer using passages and relationships.
                    answer = generate_answer(question, context)
                    sources = results

            except Exception:
                app.logger.exception("Question answering failed")
                error = (
                    "Sorry, something went wrong while answering. "
                    "Please try again."
                )

    return render_template(
        "reader.html",
        book=book,
        chapters=chapters,
        answer=answer,
        sources=sources,
        question=question,
        current_chapter=current_chapter,
        error=error
    )
   
if __name__ == "__main__":
    app.run(debug=True)