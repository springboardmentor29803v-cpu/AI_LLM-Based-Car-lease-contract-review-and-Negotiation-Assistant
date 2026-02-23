import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('MARKETCHECK_API_KEY')
vin = '1HGCM82633A004352'

print(f'Testing VIN: {vin}')
print('=' * 50)

# Test 1: VIN Decode
print('\n=== 1. VIN Decode ===')
r = requests.get(f'https://api.marketcheck.com/v2/decode/car/{vin}/specs', params={'api_key': api_key}, timeout=10)
print(f'Status: {r.status_code}')
print(f'Response: {json.dumps(r.json(), indent=2)[:500]}')

# Test 2: Search by VIN
print('\n=== 2. Search by VIN ===')
r = requests.get('https://api.marketcheck.com/v2/search/car/active', params={'api_key': api_key, 'vin': vin}, timeout=10)
print(f'Status: {r.status_code}')
data = r.json()
print(f'Listings found: {data.get("num_found", 0)}')
if data.get('listings'):
    print(f'First listing: {json.dumps(data["listings"][0], indent=2)[:400]}')

# Test 3: Get vehicle info from VIN decode and search listings
print('\n=== 3. Search Similar Vehicles ===')
# Decode VIN first to get make/model/year
decode_r = requests.get(f'https://api.marketcheck.com/v2/decode/car/{vin}/specs', params={'api_key': api_key}, timeout=10)
if decode_r.status_code == 200:
    specs = decode_r.json()
    make = specs.get('make', 'Honda')
    model = specs.get('model', 'Accord')
    year = specs.get('year', '2003')
    print(f'Decoded: {year} {make} {model}')
    
    # Search for similar
    r = requests.get('https://api.marketcheck.com/v2/search/car/active', 
                     params={'api_key': api_key, 'make': make, 'model': model, 'year': year, 'rows': 5}, timeout=10)
    print(f'Status: {r.status_code}')
    data = r.json()
    print(f'Similar listings found: {data.get("num_found", 0)}')
    if data.get('listings'):
        for i, listing in enumerate(data['listings'][:3]):
            print(f'  {i+1}. ${listing.get("price", "N/A")} - {listing.get("miles", "N/A")} miles')

# Test 4: Price Prediction
print('\n=== 4. Price Prediction ===')
r = requests.get('https://api.marketcheck.com/v2/predict/car/price', 
                 params={'api_key': api_key, 'vin': vin, 'miles': 150000}, timeout=10)
print(f'Status: {r.status_code}')
print(f'Response: {r.text[:300]}')
