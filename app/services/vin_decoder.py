#C:\Users\Hi\Desktop\car-contract-ai-v2\app\services\vin_lookup.py
# app/services/vin_decoder.py
import requests

def decode_vin(vin: str) -> dict:
    if not vin:
        return {}
    try:
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
        r = requests.get(url)
        result = r.json()
        data = {}
        for item in result["Results"]:
            if item["Variable"] == "Make":
                data["make"] = item["Value"]
            if item["Variable"] == "Model":
                data["model"] = item["Value"]
            if item["Variable"] == "Model Year":
                data["year"] = item["Value"]
        return data
    except:
        return {}