from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, Contract

router = APIRouter()


# ======================================
# GET CONTRACT DETAILS
# ======================================
@router.get("/{contract_id}")
def get_contract(contract_id: int, db: Session = Depends(get_db)):

    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    return {
        "id": contract.id,

        # 🚗 VEHICLE
        "vehicle_make": contract.vehicle_make,
        "vehicle_model": contract.vehicle_model,
        "vehicle_year": contract.vehicle_year,
        "vin": contract.vin,

        # 💰 FINANCIAL
        "apr": contract.apr or 0,
        "lease_term_months": contract.lease_term_months or 0,
        "monthly_payment": contract.monthly_payment or 0,
        "down_payment": contract.down_payment or 0,
        "mileage_allowance": contract.mileage_allowance or 0,
        "dealer_price = Column":contract.dealer_price or 0
    }