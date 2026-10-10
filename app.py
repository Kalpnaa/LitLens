from flask import Flask,render_template,request
from werkzeug.utils import secure_filename
import os
import uuid
from pathlib import Path
app = Flask(__name__)

#store uploaded books
uploaded_folder = Path(app.instance_path) /"uploads"
uploaded_folder.mkdir(parents=True,exist_ok=True)

app.config["uploaded_folder"] = str(uploaded_folder)
app.config["max_content_length"] = 1024 * 1024 * 200  #200Mb file
Allowed_extension = {"pdf","txt"}

def allowed_file(filename):
    return(
        "." in filename
        and filename.split(".",1)[1].lower() in Allowed_extension
    )
    
@app.route("/")
def home():
    return """<h1>hello litlens<h1>
               <p>your spolier-aware companion</p>
               <a href="/upload">Upload a book</a>"""

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
        file.save(str(file_path))

        # Temporary confirmation; database registration comes next.
        return render_template(
            "upload.html",
            message=f"Book uploaded successfully: {original_name}",
            stored_name=stored_name,
        )

    return render_template("upload.html")
  
@app.errorhandler(413)
def file_too_large(error):
    return render_template(
        "upload.html",
        error="File is too large. The maximum size is 20 MB."
    ), 413  

if __name__ == "__main__":
    app.run(debug=True)