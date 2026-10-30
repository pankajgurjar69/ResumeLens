import pymupdf  # PyMuPDF's current public import name


def extract_text_from_pdf(path):
    """Extract selectable text from a PDF. Image-only/scanned PDFs need OCR, not included here."""
    chunks = []
    with pymupdf.open(path) as document:
        for page in document:
            chunks.append(page.get_text("text"))
    return "\n".join(chunks)
