import os
import json
import pytesseract
from pdf2image import convert_from_path
from dotenv import load_dotenv

# --- IMPORT YOUR NEW WORKERS ---
from extraction_service import run_extraction
from vehicle_api import get_vehicle_specs

load_dotenv()

# CONFIGURATION
POPPLER_PATH = r'/usr/local/bin' 
JSON_OUTPUT = "final_extracted_loans.json"

def process_file(pdf_path):
    print(f"📄 Starting: {os.path.basename(pdf_path)}")
    
    try:
        # 1. OCR PHASE (Convert PDF to Text)
        pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        text = ""
        for page in pages[:2]: 
            text += pytesseract.image_to_string(page)
        
        # 2. EXTRACTION PHASE (Using your LangChain/Pydantic Service)
        print("🧠 Running AI Extraction...")
        data = run_extraction(text)
        
        # 3. VERIFICATION PHASE (Using NHTSA API)
        if data.get('vin'):
            print(f"🔍 Verifying VIN: {data['vin']}")
            specs = get_vehicle_specs(data['vin'])
            data.update(specs)
            
        # 4. SAVE PHASE
        data['source_file'] = os.path.basename(pdf_path)
        save_to_json(data)
        print(f"✅ Successfully processed {os.path.basename(pdf_path)}")

    except Exception as e:
        print(f"❌ Error processing file: {e}")

def save_to_json(new_entry):
    all_data = []
    if os.path.exists(JSON_OUTPUT):
        with open(JSON_OUTPUT, "r") as f:
            try:
                all_data = json.load(f)
            except:
                all_data = []
    all_data.append(new_entry)
    with open(JSON_OUTPUT, "w") as f:
        json.dump(all_data, f, indent=4)

if __name__ == "__main__":
    # Point this to your actual sample file
    sample_pdf = "/Users/apoorvasingh/Desktop/car-lease-ai-assistant/loan_samples/Loan_contract_Apoorva_01.pdf"
    process_file(sample_pdf)