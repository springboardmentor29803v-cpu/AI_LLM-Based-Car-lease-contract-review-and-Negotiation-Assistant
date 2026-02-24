from fastapi import FastAPI, UploadFile, File
import os
import pdfplumber
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# 1. SETUP FOLDERS
UPLOAD_DIR = "uploaded_contracts"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 2. DATABASE CONFIGURATION
DB_CONFIG = {
    "dbname": "carlease",
    "user": "postgres",
    "password": "2427",
    "host": "localhost",
    "port": "5432"
}

def init_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Create the table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                id SERIAL PRIMARY KEY,
                filename TEXT,
                extracted_text TEXT
            )
        """)
        conn.commit()
        conn.close()
        print("--- Database Connected & Table Ready ---")
    except Exception as e:
        print(f"Database Error: {e}")

# Run setup immediately
init_db()

@app.get("/")
def home():
    return {"message": "Car Lease Assistant (PostgreSQL Version) is Running!"}

@app.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    # A. SAVE THE FILE
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # B. EXTRACT TEXT
    extracted_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
    except Exception as e:
        return {"error": f"Failed to read PDF: {str(e)}"}

    # C. SAVE TO POSTGRESQL
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Note: We use %s here instead of ?
        cursor.execute(
            "INSERT INTO contracts (filename, extracted_text) VALUES (%s, %s) RETURNING id", 
            (file.filename, extracted_text)
        )
        new_id = cursor.fetchone()[0] # Get the ID of the new row
        conn.commit()
        conn.close()
    except Exception as e:
        return {"error": f"Database Save Failed: {str(e)}"}
    
    return {
        "status": "Success",
        "contract_id": new_id,
        "filename": file.filename,
        "preview_text": extracted_text[:200] + "..."
    }