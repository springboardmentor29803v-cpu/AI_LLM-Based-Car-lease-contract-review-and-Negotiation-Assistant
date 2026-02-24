import re
import requests

# VIN regex (17 characters, excluding I, O, Q)
VIN_REGEX = r"\b[A-HJ-NPR-Z0-9]{17}\b"


def extract_vin_from_text(text: str):
    matches = re.findall(VIN_REGEX, text)
    if matches:
        return matches[0]
    return None


def decode_vin(vin: str):
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
    response = requests.get(url)
    data = response.json()

    result = {}
    for item in data.get("Results", []):
        if item["Variable"] == "Make":
            result["make"] = item["Value"]
        if item["Variable"] == "Model":
            result["model"] = item["Value"]
        if item["Variable"] == "Model Year":
            result["year"] = item["Value"]

    return result


def fetch_recalls(make: str, model: str, year: str):
    url = f"https://api.nhtsa.gov/recalls/recallsByVehicle?make={make}&model={model}&modelYear={year}"
    response = requests.get(url)
    data = response.json()

    recalls = data.get("results", [])
    return len(recalls)


def get_full_vin_report(vin: str):
    vehicle_data = decode_vin(vin)

    if not vehicle_data.get("make"):
        return {"error": "Invalid VIN"}

    recall_count = fetch_recalls(
        vehicle_data.get("make"),
        vehicle_data.get("model"),
        vehicle_data.get("year"),
    )

    vehicle_data["vin"] = vin
    vehicle_data["recall_count"] = recall_count

    return vehicle_data
