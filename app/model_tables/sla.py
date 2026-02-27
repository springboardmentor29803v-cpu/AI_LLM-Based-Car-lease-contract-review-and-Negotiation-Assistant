# app/model_tables/sla.py

from typing import Optional
from pydantic import BaseModel, Field


class SLAData(BaseModel):

    # ----------------------
    # Vehicle Info
    # ----------------------
    vin: Optional[str] = Field(None, description="Vehicle Identification Number")
    vehicle_year: Optional[int] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None

    # ----------------------
    # Financial
    # ----------------------
    interest_rate: Optional[float] = Field(None, description="APR or interest rate")
    monthly_payment: Optional[float] = None
    down_payment: Optional[float] = None
    total_amount_financed: Optional[float] = None
    residual_value: Optional[float] = None
    buyout_price: Optional[float] = None

    # ----------------------
    # Lease Terms
    # ----------------------
    lease_term_months: Optional[int] = None
    mileage_allowance: Optional[int] = None

    # ----------------------
    # Legal / Clauses
    # ----------------------
    early_termination_clause: Optional[str] = None
    purchase_option: Optional[str] = None

    # ----------------------
    # Meta
    # ----------------------
    extraction_method: Optional[str] = None
    confidence_score: Optional[int] = None