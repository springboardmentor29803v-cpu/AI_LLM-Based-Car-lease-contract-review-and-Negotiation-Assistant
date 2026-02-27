#C:\Users\Hi\Desktop\car-contract-ai-v2\app\services\marketcheck_service.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MARKETCHECK_API_KEY")
BASE_URL = "https://api.marketcheck.com/v2"


# =========================================================
# VIN DECODE
# =========================================================
def decode_vin(vin: str):

    url = f"{BASE_URL}/decode/car/{vin}/specs"
    params = {"api_key": API_KEY}

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        make = data.get("make")
        model = data.get("model")
        year = data.get("year")
        trim = data.get("trim") or ""

        if not all([make, model, year]):
            return None

        return {
            "make": make,
            "model": model,
            "year": year,
            "trim": trim
        }

    except requests.RequestException as e:
        print(f"VIN decode failed: {e}")
        return None


# =========================================================
# PRICE PREDICTION (Primary)
# =========================================================
def predict_price(make: str, model: str, year: int, trim: str = ""):

    url = f"{BASE_URL}/predict/car/price"

    params = {
        "api_key": API_KEY,
        "make": make,
        "model": model,
        "year": year,
        "miles": 50000,
        "car_type": "used"
    }

    if trim:
        params["trim"] = trim

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        return {
            "predicted_price": float(data.get("predicted_price", 0)),
            "min_price": float(data.get("price_range", {}).get("min", 0)),
            "max_price": float(data.get("price_range", {}).get("max", 0))
        }

    except requests.RequestException as e:
        print(f"⚠️ Prediction failed — using listings fallback: {e}")
        return search_listings_price(make, model, year)


# =========================================================
# LISTINGS SEARCH (Fallback — VERY RELIABLE)
# =========================================================
def search_listings_price(make: str, model: str, year: int):

    url = f"{BASE_URL}/search/car/active"

    params = {
        "api_key": API_KEY,
        "make": make,
        "model": model,
        "year": year,
        "rows": 50
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        listings = data.get("listings", [])

        if not listings:
            return {"predicted_price": 0, "min_price": 0, "max_price": 0}

        prices = [
            float(car.get("price", 0))
            for car in listings
            if car.get("price")
        ]

        if not prices:
            return {"predicted_price": 0, "min_price": 0, "max_price": 0}

        avg_price = sum(prices) / len(prices)

        return {
            "predicted_price": avg_price,
            "min_price": min(prices),
            "max_price": max(prices)
        }

    except requests.RequestException as e:
        print(f"Listings search failed: {e}")
        return {"predicted_price": 0, "min_price": 0, "max_price": 0}