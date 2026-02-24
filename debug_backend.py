import os
import pytesseract
from pdf2image import convert_from_path
from google import genai
from google.genai import types  # <--- Add this line!
from dotenv import load_dotenv
load_dotenv()

# Setup
PDF_PATH = "/Users/apoorvasingh/Desktop/car-lease-ai-assistant/loan_samples/Loan_contract_Apoorva_01.pdf"

# Make sure POPPLER_PATH is defined if it's not in your system PATH
POPPLER_PATH = r'/usr/local/bin' 

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(api_version='v1')
)

def debug_extraction():
    print("1. Converting Page 1 to Image...")
    # Added poppler_path here just in case
    pages = convert_from_path(PDF_PATH, first_page=1, last_page=1, poppler_path=POPPLER_PATH)
    
    print("2. Running OCR on Page 1...")
    text = pytesseract.image_to_string(pages[0])
    clean_text = text[:2000] 

    print(f"3. Sending {len(clean_text)} characters to Gemini 2.0...")
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=f"Return JSON for: apr, vin, monthly_payment. Text: {clean_text}"
        )
        print("\n--- SUCCESS! AI RESPONSE ---")
        print(response.text)
    except Exception as e:
        print(f"\n--- FAILED ---")
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_extraction()