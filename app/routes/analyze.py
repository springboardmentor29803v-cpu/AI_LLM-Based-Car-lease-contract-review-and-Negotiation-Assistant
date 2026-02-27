# app/routes/analyze.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db, Contract

router = APIRouter()


@router.get("/{contract_id}")
async def analyze_contract(contract_id: int,
                           db: Session = Depends(get_db)):

    contract = db.query(Contract).filter(
        Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(status_code=404,
                            detail="Contract not found")

    # ====================================
    # CONTRACT DATA (for dashboard)
    # ====================================
    contract_data = {
        "vehicle_make": contract.vehicle_make,
        "vehicle_model": contract.vehicle_model,
        "vehicle_year": contract.vehicle_year,
        "lease_term_months": contract.lease_term_months or 0,
        "apr": contract.apr or 0.0,
        "monthly_payment": contract.monthly_payment or 0.0,
        "down_payment": contract.down_payment or 0.0,
        "mileage_allowance": contract.mileage_allowance or 0
    }

    # ====================================
    # FAIRNESS LOGIC (simple but correct)
    # ====================================

    try:
        apr = float(contract.apr or 0)
    except:
        apr = 0

    score = 100

    if apr > 10:
        score -= 25
    elif apr > 7:
        score -= 10

    if contract.monthly_payment in [None, "", 0, "0"]:
        score -= 5

    # Risk level
    if score >= 85:
        risk = "Low"
    elif score >= 60:
        risk = "Moderate"
    else:
        risk = "High"

    # Negotiation strength
    if score >= 85:
        strength = "Limited"
    elif score >= 60:
        strength = "Moderate"
    else:
        strength = "Strong"

    fairness = {
        "fairness_score": score,
        "risk_level": risk,
        "negotiation_strength": strength
    }

    # ====================================
    # IMPORTANT: EXACT FORMAT Streamlit needs
    # ====================================
    return {
        "success": True,
        "contract_data": contract_data,
        "fairness": fairness
    }