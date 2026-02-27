# app/routes/market_price.py
from fastapi import APIRouter, HTTPException
from app.database import Contract, SessionLocal
from app.services.marketcheck_service import decode_vin, predict_price
from app.utils.currency import to_inr

router = APIRouter()


@router.get("/{contract_id}/market-price")
def get_market_price(contract_id: int):

    db = SessionLocal()

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(404, "Contract not found")

    vin = contract.vin or "N/A"

    # ===============================
    # VIN DECODE
    # ===============================
    decoded = decode_vin(vin)

    if decoded:
        make = decoded["make"]
        model = decoded["model"]
        year = decoded["year"]
        trim = decoded.get("trim", "")
    else:
        make = contract.vehicle_make or "Unknown"
        model = contract.vehicle_model or "Unknown"
        year = contract.vehicle_year or 2015
        trim = ""

    # ===============================
    # CONTRACT PRICE (AUTO INR)
    # ===============================
    down = to_inr(contract.down_payment)
    monthly = to_inr(contract.monthly_payment)
    term = contract.lease_term_months or 36

    contract_price = int(down + (monthly * term))

    # ===============================
    # MARKET PRICE FROM API (USD → INR)
    # ===============================
    price_data = predict_price(make, model, year, trim)

    market_price = int(price_data["predicted_price"] * 83)
    min_price = int(price_data["min_price"] * 83)
    max_price = int(price_data["max_price"] * 83)

    # ===============================
    # FAIRNESS SCORE
    # ===============================
    diff = contract_price - market_price

    if diff <= 0:
        fairness = 90
    elif diff < 200000:
        fairness = 70
    else:
        fairness = 40

    return {
        "success": True,
        "vin": vin,
        "make": make,
        "model": model,
        "year": year,
        "contract_price_inr": contract_price,
        "market_price_inr": market_price,
        "min_price_inr": min_price,
        "max_price_inr": max_price,
        "fairness_score": fairness
    }