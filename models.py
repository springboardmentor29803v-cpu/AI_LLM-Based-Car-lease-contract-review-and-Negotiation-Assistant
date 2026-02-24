from pydantic import BaseModel, Field
from typing import Optional

class LeaseContract(BaseModel):
    apr: str = Field(description="The annual percentage rate, e.g., 5.2%")
    lease_term_months: str = Field(description="Total duration of the lease in months")
    monthly_payment: str = Field(description="Monthly payment amount including currency symbol")
    vin: str = Field(description="The 17-character Vehicle Identification Number")
    make: Optional[str] = Field(None, description="Car manufacturer")
    model: Optional[str] = Field(None, description="Car model")