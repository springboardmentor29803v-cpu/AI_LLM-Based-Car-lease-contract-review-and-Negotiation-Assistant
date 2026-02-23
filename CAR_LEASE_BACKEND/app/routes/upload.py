import os
import json
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, HTTPException
from sqlalchemy import text
from database import SessionLocal
from app.services.extraction import (
    extract_text_with_langchain,
    extract_vin_from_text,
    fetch_vehicle_data_from_nhtsa
)
from app.services.sla_extraction import extract_sla_fields
from app.services.rule_processor import RuleProcessor
from app.services.rules_cache import get_cached_rules
from app.services.market_service import MarketAnalysisService
from app.models.sla import SLAData

router = APIRouter()

# Initialize rule processor for issue detection
rule_processor = RuleProcessor()

# Initialize market analysis service
market_analysis_service = MarketAnalysisService()


def process_contract_data(raw_text: str) -> dict:
    """
    Process raw contract text to extract SLA and vehicle data.

    Args:
        raw_text: Extracted text from PDF

    Returns:
        Combined JSON with sla, vehicle, issues, market_analysis, and processed_at fields
    """
    # Extract SLA data using LangChain structured output
    sla_dict = {}
    try:
        sla_data: SLAData = extract_sla_fields(raw_text)
        sla_dict = sla_data.model_dump()
        print("✓ SLA data extracted successfully")
    except Exception as e:
        print(f"⚠ SLA extraction failed: {e}")
        sla_dict = {"error": str(e)}

    # Extract VIN and fetch vehicle data from NHTSA
    vehicle_dict = {}
    try:
        vin = extract_vin_from_text(raw_text)
        if vin:
            print(f"✓ VIN extracted: {vin}")
            vehicle_dict = fetch_vehicle_data_from_nhtsa(vin)
            print(f"✓ Vehicle data fetched from NHTSA")
        else:
            print("⚠ No valid VIN found in document")
            vehicle_dict = {"error": "No valid VIN found in document", "vin": None}
    except Exception as e:
        print(f"⚠ Vehicle data extraction failed: {e}")
        vehicle_dict = {"error": str(e), "vin": None}

    # Detect issues using rule processor
    issues = []
    try:
        rules = get_cached_rules()
        if rules and sla_dict and "error" not in sla_dict:
            issues = rule_processor.detect_issues(sla_dict, rules)
            print(f"✓ Issues detected: {len(issues)}")
    except Exception as e:
        print(f"⚠ Issue detection failed: {e}")

    # Perform market analysis
    market_analysis = None
    try:
        if sla_dict and "error" not in sla_dict and vehicle_dict and "error" not in vehicle_dict:
            # Build temporary combined data for market analysis
            temp_combined = {
                "sla": sla_dict,
                "vehicle": vehicle_dict
            }
            analysis_result = market_analysis_service.analyze_contract(temp_combined)
            market_analysis = analysis_result.model_dump()
            print(f"✓ Market analysis completed")
    except Exception as e:
        print(f"⚠ Market analysis failed: {e}")

    # Combine into single JSON object
    combined_data = {
        "sla": sla_dict,
        "vehicle": vehicle_dict,
        "issues": issues,
        "market_analysis": market_analysis,
        "processed_at": datetime.utcnow().isoformat()
    }

    return combined_data


@router.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    """
    Upload PDF contract, extract text, process SLA & vehicle data, and store in PostgreSQL.

    Full Processing Pipeline:
    1. Save uploaded file to contracts/
    2. Extract text using LangChain (with OCR fallback)
    3. Extract SLA data using LangChain with structured output
    4. Extract VIN from text using regex
    5. Call NHTSA VIN API for vehicle details
    6. Detect issues using rule processor
    7. Perform market analysis (pricing, fairness score)
    8. Combine all data into single JSON
    9. Store combined JSON in database
    10. Return combined JSON as API response
    """
    db = None
    try:
        # Step 1: Generate safe filename
        safe_name = file.filename.replace(" ", "_")

        # Step 2: Save file to contracts/
        contracts_dir = "contracts"
        os.makedirs(contracts_dir, exist_ok=True)
        file_path = os.path.join(contracts_dir, safe_name)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        print(f"✓ File saved: {file_path}")

        # Step 3: Extract text using LangChain
        docs = extract_text_with_langchain(file_path)

        # Step 4: Combine all pages into raw_text
        raw_text = "\n".join(d.page_content for d in docs)

        # Step 5: Clean extracted text (remove null bytes)
        extracted_text = raw_text.replace("\x00", "")

        print(f"✓ Text extracted: {len(extracted_text)} characters")

        # Step 6: Process contract data (SLA + Vehicle + Issues + Market Analysis)
        combined_data = process_contract_data(extracted_text)

        # Step 7: Insert into PostgreSQL with combined_data
        db = SessionLocal()
        result = db.execute(
            text("""
                INSERT INTO contracts (filename, raw_text, combined_data)
                VALUES (:f, :t, :c)
                RETURNING id
            """),
            {
                "f": safe_name,
                "t": extracted_text,
                "c": json.dumps(combined_data)
            }
        )
        document_id = result.fetchone()[0]
        db.commit()

        print(f"✓ Stored in database: ID {document_id}, filename: {safe_name}")

        # Step 8: Return combined JSON response
        return {
            "message": "Uploaded & fully processed",
            "document_id": document_id,
            "filename": safe_name,
            "characters": len(extracted_text),
            "data": combined_data
        }

    except Exception as e:
        # Error handling
        print("UPLOAD ERROR:", repr(e))
        return {"error": str(e)}

    finally:
        if db:
            db.close()


@router.get("/contract/{contract_id}")
async def get_contract_data(contract_id: int):
    """
    Get all extracted data for a contract including:
    - SLA data (terms, payments, etc.)
    - Vehicle data (make, model, VIN info)
    - Detected issues
    - Market analysis (pricing, fairness scores)

    Returns all data stored in the combined_data JSONB field.
    """
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                SELECT filename, combined_data, created_at
                FROM contracts
                WHERE id = :id
            """),
            {"id": contract_id}
        ).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")

        filename, combined_data, created_at = result

        return {
            "contract_id": contract_id,
            "filename": filename,
            "created_at": str(created_at) if created_at else None,
            "data": combined_data if combined_data else {}
        }

    finally:
        db.close()


@router.get("/contract/{contract_id}/market-analysis")
async def get_market_analysis(contract_id: int):
    """
    Get market analysis for a specific contract.

    Returns:
    - Contract price vs market prices (MarketCheck, Auto.dev, CarQuery)
    - Expected vs actual monthly payments
    - Cost breakdown (vehicle price, interest, fees)
    - Fairness score (0-100) with factor breakdown
    - Vehicle information
    """
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                SELECT combined_data
                FROM contracts
                WHERE id = :id
            """),
            {"id": contract_id}
        ).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")

        combined_data = result[0] if result[0] else {}
        market_analysis = combined_data.get("market_analysis")

        if not market_analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Market analysis not available for contract {contract_id}. Data may have failed to process during upload."
            )

        return {
            "contract_id": contract_id,
            "market_analysis": market_analysis
        }

    finally:
        db.close()
