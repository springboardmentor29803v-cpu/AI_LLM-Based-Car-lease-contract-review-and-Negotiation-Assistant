import requests
import json

def get_vehicle_specs(vin):
    """
    Queries the NHTSA vPIC API to decode the VIN.
    Returns a dictionary with Make, Model, and Year.
    """
    if not vin or len(vin) != 17:
        return {"error": "Invalid VIN length"}

    # NHTSA API Endpoint
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"
    
    try:
        print(f"🔍 Querying NHTSA for VIN: {vin}...")
        response = requests.get(url, timeout=10)
        results = response.json().get('Results', [])
        data = response.json()
        
        # Results are usually the first item in the 'Results' list
        specs = data.get('Results', [{}])[0]
        
        return {
            "vin": vin,
            "make": specs.get("Make"),
            "model": specs.get("Model"),
            "year": specs.get("ModelYear"),
            "drive_type": specs.get("DriveType"),
            "engine_hp": specs.get("EngineHP"),
            "fuel_type": specs.get("FuelTypePrimary")
        }
    except Exception as e:
        print(f"Error decoding VIN: {e}")
        return {"make": "Unknown", "model": "Unknown", "year": "Unknown"}