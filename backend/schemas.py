from pydantic import BaseModel, Field
from typing import Optional

class LeaseContractSLA(BaseModel):
    """
    Updated Schema with Year and Recalls.
    """
    # ... (Previous Financial/Usage/Ownership fields remain the same) ...
    interest_rate_apr: Optional[float] = Field(None)
    lease_term_months: Optional[int] = Field(None)
    monthly_payment: Optional[float] = Field(None)
    down_payment: Optional[float] = Field(None)
    residual_value: Optional[float] = Field(None)
    mileage_allowance: Optional[str] = Field(None)
    mileage_overage_charge: Optional[str] = Field(None)
    buyout_price: Optional[float] = Field(None)
    early_termination_fee: Optional[str] = Field(None)
    maintenance_responsibilities: Optional[str] = Field(None)
    warranty_coverage: Optional[str] = Field(None)
    insurance_requirements: Optional[str] = Field(None)
    late_fee_policy: Optional[str] = Field(None)

    # ✅ NEW FIELDS ADDED
    vehicle_year: Optional[int] = Field(None, description="The manufacturing year of the vehicle (e.g. 2025).")
    recalls_text: Optional[str] = Field(None, description="Any mention of open recalls or recall disclosures in the text.")

    # Identity
    vin_number: Optional[str] = Field(None)
    vehicle_make: Optional[str] = Field(None)
    vehicle_model: Optional[str] = Field(None)
