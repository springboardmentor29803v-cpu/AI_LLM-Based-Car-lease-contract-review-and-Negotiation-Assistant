import easyocr
import numpy as np
import fitz  # PyMuPDF

# Initialize Reader
reader = easyocr.Reader(['en'])

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    FULL SCAN MODE:
    Scans EVERY page of the PDF. No skipping.
    """
    try:
        print(f"--- 📖 Starting Full Scan of: {pdf_path} ---")
        doc = fitz.open(pdf_path)
        full_text = ""
        total_pages = len(doc)

        print(f"Total Pages to Scan: {total_pages}")

        for i, page in enumerate(doc):
            print(f"Scanning Page {i+1} of {total_pages}...")

            # 1. Try Digital Extraction first (Best Quality)
            text = page.get_text()
            
            if len(text.strip()) > 50:
                full_text += f"\n--- PAGE {i+1} (Digital) ---\n{text}\n"
            else:
                # 2. Fallback to OCR if page is an image
                print(f"   📷 Image detected. Running OCR on Page {i+1}...")
                pix = page.get_pixmap()
                img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                
                result = reader.readtext(img_np, detail=0)
                ocr_text = " ".join(result)
                full_text += f"\n--- PAGE {i+1} (OCR) ---\n{ocr_text}\n"
            
        return full_text
        
    except Exception as e:
        print(f"Extraction Error: {e}")
        return ""
