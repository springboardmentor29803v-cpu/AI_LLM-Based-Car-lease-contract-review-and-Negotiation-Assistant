from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class SLAData(BaseModel):
    """Pydantic model for SLA (Service Level Agreement) extracted fields from car lease contracts"""
    
    model_config = ConfigDict(
        json_schema_extra={"additionalProperties": False}
    )
    
    apr: Optional[str] = None
    lease_term_months: Optional[str] = None
    monthly_payment: Optional[str] = None
    down_payment: Optional[str] = None
    residual_value: Optional[str] = None
    mileage_allowance: Optional[str] = None
    early_termination_clause: Optional[str] = None
    purchase_option: Optional[str] = None
    late_fees: Optional[str] = None
    
    # New financial fields for dealer price calculation
    cap_cost: Optional[str] = None  # Capitalized cost (vehicle price in lease)
    msrp: Optional[str] = None  # Manufacturer's Suggested Retail Price
    cap_cost_reduction: Optional[str] = None  # Down payment + trade-in + rebates
    fees_total: Optional[str] = None  # Total fees (acquisition, doc, etc.)
    money_factor: Optional[str] = None  # Lease interest rate (APR/2400)
    purchase_option_price: Optional[str] = None  # End-of-lease buyout price
    
    @field_validator('*', mode='before')
    @classmethod
    def normalize_values(cls, value):
        """Convert to string and replace rupee symbol"""
        if value is None:
            return None
        
        # Convert to string if not already (handles int, float, etc.)
        if not isinstance(value, str):
            value = str(value)
        
        # Replace rupee symbols with "Rs "
        value = value.replace('₹', 'Rs ')
        value = value.replace('\u20b9', 'Rs ')
        
        return value
