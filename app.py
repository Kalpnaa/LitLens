from flask import Flask,render_template,request,redirect,url_for
from werkzeug.utils import secure_filename
import os
import uuid
from pathlib import Path
import sqlite3
import uuid
from database import init_db,get_db_connection
from book_processor import process_book

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
        count = process_book(book_id)
        
        return redirect(
            url_for("library",message=f"Book processed successfully. {count} section saved")
        )
    
    except (ValueError,FileNotFoundError,OSError) as error:
        app.logger.warning("Book Processing failed: %s",error)
        
        return redirect(
            url_for("library",error="an unexpected error occured during processing")
        )
        
if __name__ == "__main__":
    app.run(debug=True)