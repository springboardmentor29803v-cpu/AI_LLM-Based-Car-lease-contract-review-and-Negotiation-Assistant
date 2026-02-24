from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import RawContract, SLAReport
from ocr_engine import extract_text_from_pdf
from ai_agent import extract_lease_data
from validation import validate_vin
from rules_engine import analyze_contract
from pydantic import BaseModel
from chat_agent import chat_with_contract 
import os
import datetime
from vin_service import extract_vin_from_text, get_full_vin_report


Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ChatRequest(BaseModel):
    contract_id: int
    query: str

@app.post("/upload")
async def upload_contract(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        # 1. Save File Locally
        file_location = f"temp_{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # 2. FULL SCAN (Raw Text)
        print("--- 📖 Scanning PDF... ---")
        full_text = extract_text_from_pdf(file_location)
        full_text = full_text.replace("\x00", "") 

        # 3. SAVE TO DB 1: MASTER RAW DATA
        master_record = RawContract(
            filename=file.filename,
            full_pdf_text=full_text,
            upload_date=str(datetime.datetime.now())
        )
        db.add(master_record)
        db.commit()
        db.refresh(master_record)
        print(f"✅ Saved Raw Text (ID: {master_record.id})")

        # 4. AI EXTRACTION
        print("--- 🤖 Sending to AI... ---")
        sla_data = extract_lease_data(full_text)
        
        # 5. RULES & NEGOTIATION ENGINE
        print("--- 🧠 Generating Negotiation Strategy... ---")
        risk_report = analyze_contract(sla_data)
        
        # 6. VALIDATION
        vin = sla_data.get("vin_number")

# Step 2: If AI failed, use regex from full text
        if not vin or vin == "UNKNOWN":
            vin = extract_vin_from_text(full_text)

# Step 3: If still not found
        if not vin:
            gov_check = {"message": "VIN not found in contract"}
            vin_data = {"message": "VIN not found in contract"}
        else:
            gov_check = validate_vin(vin)
            vin_data = get_full_vin_report(vin)

        # 7. SAVE TO DB 2: SLA REPORT
        sla_record = SLAReport(
            raw_contract_id=master_record.id,
            vin_number=vin,
            vehicle_make=sla_data.get("vehicle_make"),
            vehicle_model=sla_data.get("vehicle_model"),
            vehicle_year=sla_data.get("vehicle_year"),
            interest_rate_apr=sla_data.get("interest_rate_apr"),
            lease_term_months=sla_data.get("lease_term_months"),
            monthly_payment=sla_data.get("monthly_payment"),
            down_payment=sla_data.get("down_payment"),
            residual_value=sla_data.get("residual_value"),
            buyout_price=sla_data.get("buyout_price"),
            mileage_allowance=sla_data.get("mileage_allowance"),
            mileage_overage_charge=sla_data.get("mileage_overage_charge"),
            early_termination_fee=sla_data.get("early_termination_fee"),
            maintenance_responsibilities=sla_data.get("maintenance_responsibilities"),
            warranty_coverage=sla_data.get("warranty_coverage"),
            insurance_requirements=sla_data.get("insurance_requirements"),
            late_fee_policy=sla_data.get("late_fee_policy"),
            recalls_text=sla_data.get("recalls_text"),
            extracted_data=sla_data,
            gov_validation_status=gov_check,
            negotiation_points=risk_report 
        )
        
        db.add(sla_record)
        db.commit()
        print("✅ Saved SLA Report with Negotiation Strategy!")

        os.remove(file_location)

        return {
            "status": "Success",
            "contract_id": master_record.id,
            "sla_data": sla_data,
            "negotiation_strategy": risk_report,
            "validation": gov_check,
            "vin_lookup": vin_data
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

# --- CHAT ENDPOINT (THE NEW PART) ---
@app.post("/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    report = db.query(SLAReport).filter(SLAReport.raw_contract_id == request.contract_id).first()
    
    # Extract only the high-level negotiation goals from your pre-run Rules Engine
    intents = ""
    if report.negotiation_points:
        intents = "\n".join([f"- {r['issue']}: {r['negotiation_intent']}" for r in report.negotiation_points.get('risk_analysis', [])])

    context_str = f"""
    Current APR: {report.interest_rate_apr}%
    Market Benchmarks & Strategic Goals:
    {intents}
    """
    
    ai_response = chat_with_contract(context_str, request.query)
    return {"response": ai_response}
