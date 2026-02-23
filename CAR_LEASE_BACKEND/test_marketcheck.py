"""
MarketCheck API Test Script
Shows what parameters are needed and what data you get back
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('MARKETCHECK_API_KEY')

VIN = "1HGCM82633A004352"  # The valid VIN you provided

print("=" * 60)
print("MARKETCHECK API TEST")
print("=" * 60)

# ============ TEST 1: VIN DECODE ============
print("\n1. VIN DECODE")
print("-" * 40)
print(f"Input: VIN = {VIN}")
r = requests.get(
    f'https://api.marketcheck.com/v2/decode/car/{VIN}/specs',
    params={'api_key': api_key},
    timeout=15
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print("Output:")
    print(f"  Year: {data.get('year')}")
    print(f"  Make: {data.get('make')}")
    print(f"  Model: {data.get('model')}")
    print(f"  Trim: {data.get('trim')}")
    print(f"  Engine: {data.get('engine')}")
    print(f"  Transmission: {data.get('transmission')}")
    print(f"  Drivetrain: {data.get('drivetrain')}")
    print(f"  Body Type: {data.get('body_type')}")
    print(f"  MPG City: {data.get('city_mpg')}")
    print(f"  MPG Highway: {data.get('highway_mpg')}")
    YEAR = data.get('year')
    MAKE = data.get('make')
    MODEL = data.get('model')
    TRIM = data.get('trim')
else:
    print(f"Error: {r.text}")
    YEAR, MAKE, MODEL, TRIM = "2003", "Honda", "Accord", "EX"

# ============ TEST 2: SEARCH LISTINGS ============
print("\n2. SEARCH LISTINGS (Similar Vehicles)")
print("-" * 40)
print(f"Input: make={MAKE}, model={MODEL}, year={YEAR}")
r = requests.get(
    'https://api.marketcheck.com/v2/search/car/active',
    params={
        'api_key': api_key,
        'make': MAKE,
        'model': MODEL,
        'year': YEAR,
        'rows': 5,
        'sort_by': 'price',
        'sort_order': 'asc'
    },
    timeout=15
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Output:")
    print(f"  Total Listings Found: {data.get('num_found')}")
    listings = data.get('listings', [])
    if listings:
        prices = [l.get('price') for l in listings if l.get('price')]
        print(f"  Sample Prices: {prices}")
        print(f"  Sample Listing:")
        l = listings[0]
        print(f"    Price: ${l.get('price')}")
        print(f"    Miles: {l.get('miles')}")
        print(f"    Heading: {l.get('heading')}")
        print(f"    Dealer: {l.get('dealer', {}).get('name', 'N/A')}")
else:
    print(f"Error: {r.text}")

# ============ TEST 3: PRICE PREDICTION ============
print("\n3. PRICE PREDICTION")
print("-" * 40)
print(f"Input: make={MAKE}, model={MODEL}, year={YEAR}, trim={TRIM}, miles=50000, car_type=used")
r = requests.get(
    'https://api.marketcheck.com/v2/predict/car/price',
    params={
        'api_key': api_key,
        'make': MAKE,
        'model': MODEL,
        'year': YEAR,
        'trim': TRIM if TRIM else 'Base',
        'miles': 50000,
        'car_type': 'used'
    },
    timeout=15
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Output:")
    print(f"  Predicted Price: ${data.get('predicted_price')}")
    price_range = data.get('price_range', {})
    print(f"  Price Range: ${price_range.get('lower_bound')} - ${price_range.get('upper_bound')}")
else:
    print(f"Error: {r.text}")

# ============ TEST 4: MARKET ANALYTICS ============
print("\n4. MARKET ANALYTICS (US Market)")
print("-" * 40)
print(f"Input: make={MAKE}, model={MODEL}, year={YEAR}")
r = requests.get(
    'https://api.marketcheck.com/v2/predict/car/us/marketcheck_price',
    params={
        'api_key': api_key,
        'make': MAKE,
        'model': MODEL,
        'year': YEAR
    },
    timeout=15
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Output:")
    print(json.dumps(data, indent=2)[:500])
else:
    print(f"Error: {r.text}")

print("\n" + "=" * 60)
print("SUMMARY OF REQUIRED PARAMETERS")
print("=" * 60)
print("""
1. VIN DECODE:
   Required: api_key, vin (in URL path)
   Returns: year, make, model, trim, engine, transmission, mpg

2. SEARCH LISTINGS:
   Required: api_key
   Optional: make, model, year, rows, sort_by, sort_order
   Returns: num_found, listings[] with price, miles, dealer info

3. PRICE PREDICTION:
   Required: api_key, make, model, year, trim, miles, car_type
   Returns: predicted_price, price_range (lower_bound, upper_bound)

4. MARKET ANALYTICS:
   Required: api_key, make, model, year
   Returns: average_price, price statistics
""")
