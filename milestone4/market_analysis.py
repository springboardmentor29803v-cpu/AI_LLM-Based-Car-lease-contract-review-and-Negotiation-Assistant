import requests
import os

def get_market_data(vin: str, mileage: int = 12000) -> dict:
    api_key = os.getenv("MARKETCHECK_API_KEY")
    
    try:
        # Call 1 - Decode VIN
        decode_url = f"https://mc-api.marketcheck.com/v2/decode/car/{vin}/specs"
        decode_resp = requests.get(decode_url, params={"api_key": api_key}, timeout=10)
        print(f"Decode status: {decode_resp.status_code}")
        print(f"Decode response: {decode_resp.text[:300]}")
        
        if decode_resp.status_code == 200:
            decode_data = decode_resp.json()
            make = decode_data.get("make", "")
            model = decode_data.get("model", "")
            year = decode_data.get("year", "")
            
            
            print(f"Decoded: {year} {make} {model}")
            
            search_url = "https://mc-api.marketcheck.com/v2/search/car/active"
            search_params = {
                "api_key": api_key,
                "make": make,
                "model": model,
                "year": year,
                "rows": 5,
               
            }
            search_resp = requests.get(search_url, params=search_params, timeout=10)
            print(f"Search status: {search_resp.status_code}")
            print(f"Search response: {search_resp.text[:300]}")
            
            if search_resp.status_code == 200:
                data = search_resp.json()
                listings = data.get("listings", [])
                if listings:
                    prices = [l.get("price", 0) for l in listings if l.get("price")]
                    if prices:
                        avg_price_usd = sum(prices) / len(prices)
                        print(f"Average price USD: {avg_price_usd}")
                        return {
                            "market_price_inr": round(avg_price_usd * 80.88),
                            "vehicle_info": {"make": make, "model": model, "year": year}
                        }
    except Exception as e:
        print(f"MarketCheck error: {e}")
    
    vehicle_info = decode_vin_nhtsa(vin)
    base_price_usd = calculate_dynamic_base_price(
        vehicle_info.get('make', 'Toyota'),
        vehicle_info.get('model', 'Camry'),
        vehicle_info.get('year', 2024)
    )
    mileage_factor = max(0.6, 1 - ((mileage / 10000) * 0.015))
    market_price_inr = base_price_usd * mileage_factor * 80.88
    
    return {
        "market_price_inr": round(market_price_inr),
        "vehicle_info": vehicle_info
    }

def decode_vin_nhtsa(vin: str) -> dict:
    try:
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
        response = requests.get(url, timeout=5)
        data = response.json()
        results = {item['Variable']: item['Value'] for item in data['Results'] if item['Value']}
        return {
            'make': results.get('Make', 'Toyota'),
            'model': results.get('Model', 'Camry'),
            'year': int(results.get('Model Year', 2024))
        }
    except:
        return {'make': 'Toyota', 'model': 'Camry', 'year': 2024}

def calculate_dynamic_base_price(make: str, model: str, year: int) -> float:
    luxury_brands = {'BMW': 1.45, 'MERCEDES': 1.50, 'AUDI': 1.40, 'LEXUS': 1.35}
    factor = luxury_brands.get(make.upper(), 1.0)
    age = 2026 - year
    depreciation = max(0.4, 1 - (age * 0.05))

    return 30000 * factor * depreciation
