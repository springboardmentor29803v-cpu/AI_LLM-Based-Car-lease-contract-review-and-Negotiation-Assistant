"""
MARKETCHECK API DEMO - Show Raw API Output vs Calculated Values
Run this to demonstrate to your sir what comes from API vs what we calculate
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('MARKETCHECK_API_KEY')

VIN = "1HGCM82633A004352"

print("=" * 80)
print("MARKETCHECK API - RAW RESPONSES vs CALCULATED VALUES")
print("=" * 80)

# ============================================================================
# API CALL 1: VIN DECODE
# ============================================================================
print("\n" + "=" * 80)
print("API CALL 1: VIN DECODE")
print("=" * 80)
print(f"URL: https://api.marketcheck.com/v2/decode/car/{VIN}/specs")
print(f"Method: GET")
print(f"Parameters: api_key")

r = requests.get(
    f'https://api.marketcheck.com/v2/decode/car/{VIN}/specs',
    params={'api_key': api_key},
    timeout=15
)

print(f"\nStatus Code: {r.status_code}")
print("\n>>> RAW API RESPONSE (JSON):")
print("-" * 40)
vin_data = r.json()
print(json.dumps(vin_data, indent=2))

print("\n>>> WHAT WE EXTRACT FROM THIS:")
print("-" * 40)
print(f"  year  = {vin_data.get('year')}")
print(f"  make  = {vin_data.get('make')}")
print(f"  model = {vin_data.get('model')}")
print(f"  trim  = {vin_data.get('trim')}")

YEAR = vin_data.get('year', '2003')
MAKE = vin_data.get('make', 'Honda')
MODEL = vin_data.get('model', 'Accord')
TRIM = vin_data.get('trim', 'EX')

# ============================================================================
# API CALL 2: SEARCH LISTINGS
# ============================================================================
print("\n" + "=" * 80)
print("API CALL 2: SEARCH ACTIVE LISTINGS")
print("=" * 80)
print(f"URL: https://api.marketcheck.com/v2/search/car/active")
print(f"Method: GET")
print(f"Parameters: api_key, make={MAKE}, model={MODEL}, year={YEAR}, rows=5")

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

print(f"\nStatus Code: {r.status_code}")
print("\n>>> RAW API RESPONSE (JSON) - First 2 listings:")
print("-" * 40)
listings_data = r.json()
# Show structure with first 2 listings
display_data = {
    "num_found": listings_data.get("num_found"),
    "listings": listings_data.get("listings", [])[:2]
}
print(json.dumps(display_data, indent=2))

print("\n>>> WHAT WE EXTRACT FROM THIS:")
print("-" * 40)
print(f"  num_found (total listings) = {listings_data.get('num_found')}")
listings = listings_data.get('listings', [])
prices = [l.get('price') for l in listings if l.get('price') and l.get('price') > 0]
print(f"  prices extracted = {prices}")

# ============================================================================
# API CALL 3: PRICE PREDICTION
# ============================================================================
print("\n" + "=" * 80)
print("API CALL 3: PRICE PREDICTION (ML Model)")
print("=" * 80)
print(f"URL: https://api.marketcheck.com/v2/predict/car/price")
print(f"Method: GET")
print(f"Parameters: api_key, make={MAKE}, model={MODEL}, year={YEAR}, trim={TRIM}, miles=50000, car_type=used")

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

print(f"\nStatus Code: {r.status_code}")
print("\n>>> RAW API RESPONSE (JSON):")
print("-" * 40)
predict_data = r.json()
print(json.dumps(predict_data, indent=2))

print("\n>>> WHAT WE EXTRACT FROM THIS:")
print("-" * 40)
predicted_price = predict_data.get('predicted_price')
price_range = predict_data.get('price_range', {})
print(f"  predicted_price = ${predicted_price}")
print(f"  lower_bound     = ${price_range.get('lower_bound')}")
print(f"  upper_bound     = ${price_range.get('upper_bound')}")

# ============================================================================
# WHAT WE CALCULATE (NOT FROM API)
# ============================================================================
print("\n" + "=" * 80)
print("VALUES WE CALCULATE (NOT FROM API)")
print("=" * 80)

# Example contract values (from SLA extraction)
contract_price = 34120.0  # From cap_cost in contract
monthly_payment = 649.0   # From contract
down_payment = 3500.0     # From contract
apr = 4.99                # From contract
lease_term = 36           # From contract

print("\n>>> FROM CONTRACT (SLA Extraction):")
print("-" * 40)
print(f"  contract_price (cap_cost)  = ${contract_price}")
print(f"  monthly_payment            = ${monthly_payment}")
print(f"  down_payment               = ${down_payment}")
print(f"  apr                        = {apr}%")
print(f"  lease_term                 = {lease_term} months")

print("\n>>> CALCULATED BY OUR CODE:")
print("-" * 40)

# Market average - from API
market_average = predicted_price
print(f"  market_average = ${market_average} (from API predicted_price)")

# Market median - same as average when using prediction
market_median = predicted_price
print(f"  market_median = ${market_median} (same as predicted when no listings)")

# Typical range - from API price_range
typical_range_low = price_range.get('lower_bound')
typical_range_high = price_range.get('upper_bound')
print(f"  typical_range_low = ${typical_range_low} (from API lower_bound)")
print(f"  typical_range_high = ${typical_range_high} (from API upper_bound)")

# Expected monthly payment - WE CALCULATE THIS
if market_average and apr and lease_term:
    principal = market_average - down_payment
    monthly_rate = apr / 12 / 100
    expected_monthly = principal * monthly_rate * pow(1 + monthly_rate, lease_term) / (pow(1 + monthly_rate, lease_term) - 1)
    print(f"  expected_monthly_payment = ${expected_monthly:.2f} (CALCULATED using EMI formula)")
    print(f"    Formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)")
    print(f"    Where: P={principal}, r={monthly_rate:.6f}, n={lease_term}")

# Fairness Score - WE CALCULATE THIS
overpayment_pct = ((contract_price - market_average) / market_average) * 100
price_score = max(0, 100 - (overpayment_pct * 5)) if overpayment_pct > 0 else 100
apr_score = 100 if apr <= 6 else max(0, 100 - ((apr - 6) * 5))
fairness_score = (price_score * 0.30 + apr_score * 0.30 + 90 * 0.20 + 90 * 0.20)
print(f"\n  fairness_score = {fairness_score:.2f} (CALCULATED)")
print(f"    price_score = {price_score:.2f} (contract vs market)")
print(f"    apr_score = {apr_score:.2f} (based on APR)")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY: API DATA vs CALCULATED DATA")
print("=" * 80)

print("""
┌─────────────────────────────────────┬────────────────────────────────────────┐
│ FROM MARKETCHECK API                │ CALCULATED BY OUR CODE                 │
├─────────────────────────────────────┼────────────────────────────────────────┤
│ predicted_price → market_average    │ expected_monthly_payment (EMI formula) │
│ lower_bound → typical_range_low     │ fairness_score (weighted formula)      │
│ upper_bound → typical_range_high    │ price_score (overpayment %)            │
│ listings[] → prices for statistics  │ apr_score (rate comparison)            │
│ year, make, model, trim (VIN decode)│ fees_score, term_score                 │
│                                     │ market_median (from listings if avail) │
│                                     │ interest_cost (total - principal)      │
└─────────────────────────────────────┴────────────────────────────────────────┘
""")

print("\nData Sources in final output: ['MarketCheck Price Prediction']")
