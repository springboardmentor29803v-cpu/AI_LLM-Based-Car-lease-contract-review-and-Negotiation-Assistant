# app/schemas.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContractBase(BaseModel):
    filename: str
    file_path: str
    file_size: int
    original_content: str


class ContractCreate(ContractBase):
    pass


class Contract(ContractBase):
    id: int
    upload_date: datetime
    status: str

    # Vehicle fields
    vin: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[str] = None

    # Financial fields
    annual_percentage_rate: Optional[str] = None
    monthly_payment: Optional[str] = None
    total_amount_financed: Optional[str] = None
    down_payment: Optional[str] = None
    residual_value: Optional[str] = None
    mileage_allowance: Optional[str] = None
    lease_term: Optional[str] = None
    interest_rate: Optional[str] = None

    # Other
    early_termination_clause: Optional[str] = None
    purchase_option: Optional[str] = None

    class Config:
        from_attributes = True


class ExtractionResult(BaseModel):
    vin: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[str] = None

    annual_percentage_rate: Optional[str] = None
    monthly_payment: Optional[str] = None
    total_amount_financed: Optional[str] = None
    down_payment: Optional[str] = None
    residual_value: Optional[str] = None
    mileage_allowance: Optional[str] = None
    lease_term: Optional[str] = None
    interest_rate: Optional[str] = None