# app/routes/upload.py
# app/routes/upload.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import shutil
import uuid
import PyPDF2

from app.database import get_db, Contract
from app.services.llm_extractor import LLMExtractor

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

extractor = LLMExtractor()


# =========================
# PDF TEXT EXTRACTION
# =========================
def extract_text_from_pdf(path: str) -> str:

    text = ""

    try:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t

    except Exception as e:
        print("PDF read error:", e)

    return text.replace("\x00", "").strip()


# =========================
# UPLOAD CONTRACT API
# =========================
@router.post("/upload")
async def upload_contract(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # ✔ Ensure file exists
    if not file:
        raise HTTPException(400, "No file uploaded")

    # ✔ Ensure PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files allowed")

    # Save file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    text = extract_text_from_pdf(file_path)

    if not text:
        print("⚠️ No text extracted from PDF")

    # Extract fields (safe)
    try:
        data = extractor.extract(text)
    except Exception as e:
        print("Extraction error:", e)
        data = {}

    print("📄 Extracted:", data)

    # Save to DB
    contract = Contract(
        filename=file.filename,
        file_path=file_path,
        raw_text=text,

        vin=data.get("vin"),
        vehicle_make=data.get("vehicle_make"),
        vehicle_model=data.get("vehicle_model"),
        vehicle_year=data.get("vehicle_year"),

        dealer_price=data.get("dealer_price"),
        apr=data.get("apr"),
        lease_term_months=data.get("lease_term_months"),
        monthly_payment=data.get("monthly_payment"),
        down_payment=data.get("down_payment"),
        mileage_allowance=data.get("mileage_allowance"),

        status="uploaded"
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)

    return {
        "success": True,
        "contract_id": contract.id,
        "contract_data": data
    }