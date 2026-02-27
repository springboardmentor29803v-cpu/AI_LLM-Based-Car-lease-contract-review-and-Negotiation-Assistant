# app/services/ocr_service.py - SIMPLE OCR SERVICE
# app/services/ocr_service.py
import pytesseract
from pdf2image import convert_from_path
import re
from typing import Optional

# ⭐ If Windows, set this if pytesseract not in PATH
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Convert PDF to images, then OCR each page.
    Returns full concatenated text.
    """
    try:
        pages = convert_from_path(pdf_path, dpi=300)
        text = ""
        for i, page in enumerate(pages):
            page_text = pytesseract.image_to_string(page)
            text += page_text + "\n"
        return clean_text(text)
    except Exception as e:
        print("OCR ERROR:", e)
        return ""

def clean_text(text: str) -> str:
    """Clean OCR text for consistent regex extraction."""
    if not text:
        return ""
    # Remove null chars, multiple spaces, merge broken words
    text = text.replace("\x00", "")
    text = re.sub(r"(\b[A-Z])\s+([a-z])", r"\1\2", text)
    text = re.sub(r"(\b[A-Z])\s+([A-Z][a-z])", r"\1\2", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()