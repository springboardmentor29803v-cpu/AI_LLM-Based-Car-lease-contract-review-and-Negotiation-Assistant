# app/services/regex_extractor.py
import re


def regex_extract(text: str) -> dict:

    def find(pattern, cast=float):
        m = re.search(pattern, text, re.IGNORECASE)
        if not m:
            return None
        try:
            return cast(m.group(1).replace(",", ""))
        except:
            return None

    vin_match = re.search(r"\b([A-HJ-NPR-Z0-9]{17})\b", text)

    return {

        "vin": vin_match.group(1) if vin_match else None,

        # --- PAYMENTS ---
        "monthly_payment":
            find(r"(?:Monthly Payment|Monthly Installment|EMI)[:\s₹$]*([\d,]+)"),

        "down_payment":
            find(r"(?:Down Payment|Cap Cost Reduction|Initial Payment)[:\s₹$]*([\d,]+)"),

        "dealer_price":
            find(r"(?:Total Price|Vehicle Price|MSRP|Selling Price)[:\s₹$]*([\d,]+)"),

        # --- RATE ---
        "apr":
            find(r"(?:APR|Interest Rate|Rate)[:\s]*([\d.]+)"),

        # --- TERM ---
        "lease_term_months":
            find(r"(?:Lease Term|Term)[:\s]*(\d+)\s*(?:months|mo)", int),

        # --- MILEAGE ---
        "mileage_allowance":
            find(r"(?:Mileage|Miles per Year|Annual Mileage)[:\s]*([\d,]+)", int),

        # --- VEHICLE ---
        "vehicle_year":
            find(r"\b(20\d{2})\b", int),

        "vehicle_make": None,
        "vehicle_model": None
    }