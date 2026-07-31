import os

import PyPDF2

try:
    import pdfplumber  # type: ignore
except Exception:  # pragma: no cover
    pdfplumber = None


def extract_text_from_pdf(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError("PDF file was not found")

    text_chunks = []

    if pdfplumber is not None:
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    if text.strip():
                        text_chunks.append(text.strip())
        except Exception:
            text_chunks = []

    if not text_chunks:
        reader = PyPDF2.PdfReader(file_path)
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                text_chunks.append(text.strip())

    return "\n".join(text_chunks)
