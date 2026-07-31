import os
import re
import sqlite3
import tempfile
from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request, send_file, url_for, flash

from models.keyword import extract_keywords
from models.preprocess import estimate_reading_time, preprocess_text
from models.summarizer import summarize_text
from utils.doc_reader import extract_text_from_docx, extract_text_from_pptx
from utils.exporter import export_summary_docx, export_summary_pdf
from utils.pdf_reader import extract_text_from_pdf

app = Flask(__name__)
app.config["SECRET_KEY"] = "ai-summarizer-secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
DB_PATH = os.path.join(BASE_DIR, "database", "history.db")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_text TEXT NOT NULL,
            summary TEXT NOT NULL,
            keywords TEXT NOT NULL,
            created_at TEXT NOT NULL,
            reading_time TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            char_count INTEGER NOT NULL,
            model_name TEXT NOT NULL,
            length TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


def write_log(message):
    with open(os.path.join(OUTPUT_FOLDER, "processing.log"), "a", encoding="utf-8") as handle:
        handle.write(f"[{datetime.utcnow().isoformat()}] {message}\n")


def save_summary(filename, original_text, summary, keywords, reading_time, word_count, char_count, model_name, length):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO summaries (filename, original_text, summary, keywords, created_at, reading_time, word_count, char_count, model_name, length)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            filename,
            original_text,
            summary,
            ", ".join(keywords),
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            reading_time,
            word_count,
            char_count,
            model_name,
            length,
        ),
    )
    summary_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return summary_id


def get_history(limit=50):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """
        SELECT id, filename, summary, keywords, created_at, reading_time, word_count, char_count, model_name, length
        FROM summaries
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "filename": row[1],
            "summary": row[2],
            "keywords": row[3],
            "created_at": row[4],
            "reading_time": row[5],
            "word_count": row[6],
            "char_count": row[7],
            "model_name": row[8],
            "length": row[9],
        }
        for row in rows
    ]


def get_summary_by_id(summary_id):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        """
        SELECT id, filename, original_text, summary, keywords, created_at, reading_time, word_count, char_count, model_name, length
        FROM summaries
        WHERE id = ?
        """,
        (summary_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "filename": row[1],
        "original_text": row[2],
        "summary": row[3],
        "keywords": row[4],
        "created_at": row[5],
        "reading_time": row[6],
        "word_count": row[7],
        "char_count": row[8],
        "model_name": row[9],
        "length": row[10],
    }


def delete_summary(summary_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM summaries WHERE id = ?", (summary_id,))
    conn.commit()
    conn.close()


def slugify(value):
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-")
    return value or "summary"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    history = get_history()
    return render_template("dashboard.html", history=history)


@app.route("/summarize", methods=["POST"])
def summarize():
    uploaded_file = request.files.get("file")
    pasted_text = request.form.get("text", "").strip()
    length = request.form.get("length", "medium").lower()
    model_name = request.form.get("model", "bart").lower()

    source_text = ""
    filename = "Paste Text"

    if uploaded_file and uploaded_file.filename:
        filename = uploaded_file.filename
        extension = os.path.splitext(filename)[1].lower()
        allowed_types = {".pdf", ".docx", ".ppt", ".pptx", ".txt"}
        if extension not in allowed_types:
            return jsonify({"success": False, "message": "Unsupported file type. Please upload PDF, DOCX, or TXT."})

        if uploaded_file.content_length and uploaded_file.content_length > 10 * 1024 * 1024:
            return jsonify({"success": False, "message": "File is too large. Please upload a file smaller than 10MB."})

        temp_path = os.path.join(UPLOAD_FOLDER, f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}")
        uploaded_file.save(temp_path)
        try:
            if extension == ".pdf":
                source_text = extract_text_from_pdf(temp_path)
            elif extension in {".docx", ".pptx"}:
                if extension == ".docx":
                    source_text = extract_text_from_docx(temp_path)
                else:
                    source_text = extract_text_from_pptx(temp_path)
            elif extension == ".ppt":
                source_text = extract_text_from_pptx(temp_path)
            else:
                with open(temp_path, "r", encoding="utf-8", errors="ignore") as handle:
                    source_text = handle.read()
        except Exception as exc:
            write_log(f"Extraction failed for {filename}: {exc}")
            return jsonify({"success": False, "message": f"Could not process the file: {exc}"})
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    elif pasted_text:
        source_text = pasted_text
    else:
        return jsonify({"success": False, "message": "Please upload a document or paste some text."})

    if not source_text or len(source_text.strip()) < 20:
        return jsonify({"success": False, "message": "The provided content is too short to summarize."})

    cleaned_text = preprocess_text(source_text)
    if len(cleaned_text.split()) < 10:
        return jsonify({"success": False, "message": "The content must contain at least 10 words."})

    try:
        summary = summarize_text(cleaned_text, length=length, model_name=model_name)
        keywords = extract_keywords(cleaned_text)
        reading_time = estimate_reading_time(cleaned_text)
        word_count = len(cleaned_text.split())
        char_count = len(cleaned_text)
    except Exception as exc:
        write_log(f"Summarization failed for {filename}: {exc}")
        return jsonify({"success": False, "message": f"The model could not generate a summary: {exc}"})

    summary_id = save_summary(
        filename=filename,
        original_text=cleaned_text,
        summary=summary,
        keywords=keywords,
        reading_time=reading_time,
        word_count=word_count,
        char_count=char_count,
        model_name=model_name,
        length=length,
    )
    write_log(f"Created summary {summary_id} for {filename} using {model_name}")

    return jsonify(
        {
            "success": True,
            "message": "Summary generated successfully.",
            "summary": summary,
            "keywords": keywords,
            "reading_time": reading_time,
            "word_count": word_count,
            "char_count": char_count,
            "summary_id": summary_id,
            "filename": filename,
            "history": get_history(),
        }
    )


@app.route("/history_data")
def history_data():
    return jsonify(get_history())


@app.route("/delete_history/<int:summary_id>", methods=["POST"])
def delete_history(summary_id):
    delete_summary(summary_id)
    return jsonify({"success": True, "message": "History deleted successfully."})


@app.route("/download/<int:summary_id>/<string:file_type>")
def download_summary(summary_id, file_type):
    entry = get_summary_by_id(summary_id)
    if not entry:
        return jsonify({"success": False, "message": "Summary not found."})

    if file_type == "pdf":
        output_path = export_summary_pdf(entry["summary"], entry["filename"])
        return send_file(output_path, as_attachment=True, download_name=f"{slugify(entry['filename'])}.pdf")

    if file_type == "docx":
        output_path = export_summary_docx(entry["summary"], entry["filename"])
        return send_file(output_path, as_attachment=True, download_name=f"{slugify(entry['filename'])}.docx")

    return jsonify({"success": False, "message": "Unsupported export format."})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)