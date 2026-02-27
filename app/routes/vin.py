# app/routes/vin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests

from app.database import get_db, Contract

router = APIRouter()


@router.get("/{contract_id}")
def vin_intelligence(contract_id: int, db: Session = Depends(get_db)):
    
    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(404, "Contract not found")

    if not contract.vin:
        raise HTTPException(400, "VIN not available")

    vin = contract.vin

    # 🔹 Call NHTSA VIN API
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vin}?format=json"

    try:
        response = requests.get(url)
        data = response.json()

        result = data["Results"][0]

    except Exception as e:
        raise HTTPException(500, f"VIN API failed: {str(e)}")

    # 🔹 Extract useful fields
    decoded = {
        "make": result.get("Make"),
        "model": result.get("Model"),
        "year": result.get("ModelYear"),
        "body_class": result.get("BodyClass"),
        "engine": result.get("EngineModel"),
        "fuel_type": result.get("FuelTypePrimary"),
        "manufacturer": result.get("Manufacturer"),
        "plant_country": result.get("PlantCountry")
    }

    return {
        "success": True,
        "vin": vin,
        "decoded_data": decoded
    }