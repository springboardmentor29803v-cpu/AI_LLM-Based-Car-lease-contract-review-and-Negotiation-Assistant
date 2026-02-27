#C:\Users\Hi\Desktop\car-contract-ai-v2\app\services\pdf_extraction.py
import pdfplumber


def extract_text_from_pdf(file_path: str) -> str:

    text = ""

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"

    except Exception as e:
        print("PDF extraction error:", e)

    return text.strip()