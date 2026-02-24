from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import datetime
from pathlib import Path

from database import SessionLocal, engine, Base
from models import RawContract, SLAReport
from ocr_engine import extract_text_from_pdf
from ai_agent import extract_lease_data
from price_agent import extract_dealer_price_from_text
from validation import validate_vin
from rules_engine import analyze_contract
from vin_service import extract_vin_from_text, get_full_vin_report
from chat_agent import ask_contract_question
from market_service import get_predicted_price, calculate_fairness, convert_to_inr

import os

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

print("KEY LOADED:", os.getenv("GROQ_API_KEY") is not None)


app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/upload")
async def upload_contract(file: UploadFile = File(...), db: Session = Depends(get_db)):

    try:
        file_location = f"temp_{file.filename}"

        with open(file_location, "wb") as f:
            f.write(await file.read())
 
        full_text = extract_text_from_pdf(file_location).replace("\x00", "")

       
        master_record = RawContract(
            filename=file.filename,
            full_pdf_text=full_text,
            upload_date=str(datetime.datetime.now())
        )
        db.add(master_record)
        db.commit()
        db.refresh(master_record)

      
        print("🚀 CALLING AI EXTRACTION...")
        sla_data = extract_lease_data(full_text[:12000])
        print("✅ AI RETURNED:", sla_data)
        print("EXTRACTED SLA DATA:", sla_data)
        risk_report = analyze_contract(sla_data)

       
        vin = sla_data.get("vin_number") or extract_vin_from_text(full_text)

        if vin:
            gov_check = validate_vin(vin)
            vin_data = get_full_vin_report(vin)
        else:
            gov_check = {"message": "VIN not found"}
            vin_data = {"message": "VIN not found"}

        
        dealer_price_data = extract_dealer_price_from_text(full_text)
        dealer_price_llm = dealer_price_data.get("dealer_price")
        dealer_price_confidence = dealer_price_data.get("confidence")


        market_average = None
        fairness_score = None
        price_difference = None
        difference_percent = None
        verdict = None

        if dealer_price_llm and sla_data.get("vehicle_make"):

            predicted = get_predicted_price(
                make=sla_data.get("vehicle_make"),
                model=sla_data.get("vehicle_model"),
                year=sla_data.get("vehicle_year"),
                trim="Base",
                miles=15000
            )


        if dealer_price_llm and sla_data.get("vehicle_make"):

            predicted = get_predicted_price(
                make=sla_data.get("vehicle_make"),
                model=sla_data.get("vehicle_model"),
                year=sla_data.get("vehicle_year"),
                trim="Base",
                miles=15000
            )

         
            if predicted:
                market_price_usd = predicted.get("predicted_price")
                currency = predicted.get("currency", "USD")
                market_average = convert_to_inr(market_price_usd, currency)
            else:
                market_average = sla_data.get("residual_value") or dealer_price_llm * 0.9

            
            if market_average:
                fairness_data = calculate_fairness(
                    contract_price=dealer_price_llm,
                    predicted_price=market_average,
                    apr=sla_data.get("interest_rate_apr") or 0,
                    fees=0,
                    term_months=sla_data.get("lease_term_months") or 36
                )

                fairness_score = fairness_data.get("final_score", 0)

                price_difference = dealer_price_llm - market_average

                difference_percent = (
                    (price_difference / market_average) * 100
                    if market_average else 0
                )

                verdict = (
                    "Excellent" if fairness_score >= 80
                    else "Fair" if fairness_score >= 60
                    else "Overpriced"
                )
     
        sla_record = SLAReport(
            raw_contract_id=master_record.id,
            filename=file.filename,
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
            extracted_data=sla_data,
            gov_validation_status=gov_check,
            negotiation_points=risk_report,
            dealer_price=dealer_price_llm,
            market_price=market_average,
            fairness_score=fairness_score,
            price_difference=price_difference,
            difference_percent=difference_percent,
            verdict=verdict
        )

        db.add(sla_record)
        db.commit()

        os.remove(file_location)

        return {
            "status": "Success",
            "contract_id": master_record.id,
            "filename": file.filename,   # ⭐ ADD THIS
            "sla_data": sla_data,
            "vin_lookup": vin_data,
            "dealer_market_price": dealer_price_llm,
            "market_average_price": market_average,
            "fairness_score": fairness_score,
            "price_difference": price_difference,
            "difference_percent": difference_percent,
            "verdict": verdict,
            "confidence": dealer_price_confidence,
            "negotiation_points": risk_report
        }

    except Exception as e:
        print("🔥 BACKEND ERROR:", e)
        return {"error": str(e)}


@app.post("/chat")
async def chat(request: dict, db: Session = Depends(get_db)):

    try:
        print("💬 CHAT REQUEST RECEIVED")

        contract_id = request.get("contract_id")
        query = request.get("query")

        if not contract_id or not query:
            return {"response": "Missing contract_id or query"}

      
        contract = db.query(SLAReport).filter(
            SLAReport.raw_contract_id == contract_id
        ).first()

        if not contract:
            return {"response": "Contract not found"}

        print("🚀 CALLING NEGOTIATION AI...")

        reply = ask_contract_question(
            query=query,
            contract_data=contract.extracted_data
        )

        return {"response": reply}

    except Exception as e:
        print("🔥 CHAT ERROR:", e)
        return {"response": "AI failed to respond"}
