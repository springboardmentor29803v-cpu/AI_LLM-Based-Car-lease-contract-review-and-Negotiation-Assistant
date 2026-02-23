import warnings
import sys
import os
from io import StringIO
warnings.filterwarnings("ignore", message="Key 'title' is not supported")
warnings.filterwarnings("ignore", message=".*title.*not supported.*")
import json
from typing import Any, Dict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError

from app.models.sla import SLAData

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Add it to your .env file.")

MODEL_ID = "gemini-2.5-flash"

# Initialize LangChain ChatGoogle LLM with structured output
# Suppress "Key 'title' is not supported" messages from google-generativeai
_old_stderr = sys.stderr
sys.stderr = StringIO()
try:
    llm = ChatGoogleGenerativeAI(model=MODEL_ID, google_api_key=GEMINI_API_KEY)
    structured_llm = llm.with_structured_output(SLAData)
finally:
    sys.stderr = _old_stderr

SLA_PROMPT = """
You are a contract analysis assistant.

Extract the following SLA fields from the contract.

Definitions:
- apr: The annual percentage rate or interest rate charged on the lease or financing.
- lease_term_months: Total length of the lease in months.
- monthly_payment: Regular periodic payment amount.
- down_payment: Upfront amount paid at lease start.
- residual_value: Buyout price or estimated vehicle value at end of lease.
- mileage_allowance: Maximum allowed mileage over the lease or per year.
- early_termination_clause: Rules, fees, or penalties for ending the lease early.
- purchase_option: Whether and how the lessee can purchase the vehicle at lease end.
- late_fees: Penalties for late payments.
- cap_cost: Capitalized cost - the negotiated price of the vehicle in the lease (may be called "Gross Cap Cost" or "Adjusted Cap Cost").
- msrp: Manufacturer's Suggested Retail Price or sticker price of the vehicle.
- cap_cost_reduction: Total of down payment, trade-in value, and any rebates applied to reduce the cap cost.
- fees_total: Total fees including acquisition fee, documentation fee, registration, taxes, etc.
- money_factor: The lease interest rate expressed as a decimal (APR divided by 2400). May appear as a small decimal like 0.00125.
- purchase_option_price: The price to buy the vehicle at the end of the lease (often equals residual value).

If a field is not explicitly present, return null.

Contract text:
{{TEXT_FROM_DB}}
"""


def _build_prompt(contract_text: str) -> str:
    return SLA_PROMPT.replace("{{TEXT_FROM_DB}}", contract_text)


def extract_sla_fields(contract_text: str) -> SLAData:
    """Extract SLA fields using LangChain's structured output approach"""
    if not contract_text or not contract_text.strip():
        raise ValueError("Contract text is empty; cannot extract SLA fields.")

    prompt = _build_prompt(contract_text)
    
    try:
        # LangChain handles schema enforcement and returns SLAData directly
        # No manual JSON parsing needed - structured_llm returns a Python object
        sla_data = structured_llm.invoke(prompt)
        print(f"[DEBUG] LLM raw response type: {type(sla_data)}")
        print(f"[DEBUG] LLM raw response: {sla_data}")
    except Exception as exc:
        raise ValueError(f"Gemini request failed: {exc}") from exc

    try:
        # Handle case where LLM returns a list instead of single object
        if isinstance(sla_data, list):
            if len(sla_data) == 0:
                raise ValueError("LLM returned empty list")
            sla_data = sla_data[0]
        
        # Handle case where response is wrapped in {'args': {...}, 'type': 'SLAData'}
        if isinstance(sla_data, dict) and 'args' in sla_data:
            sla_data = sla_data['args']
        
        # Verify it's a valid SLAData instance
        if isinstance(sla_data, SLAData):
            return sla_data
        elif isinstance(sla_data, dict):
            return SLAData(**sla_data)
        else:
            raise ValueError(f"LLM did not return SLAData instance, got {type(sla_data)}")
    except (ValidationError, TypeError) as exc:
        raise ValueError(f"Invalid SLA data: {exc}") from exc
