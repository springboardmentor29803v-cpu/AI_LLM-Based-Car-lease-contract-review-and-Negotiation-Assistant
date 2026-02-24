from sqlalchemy import Column, Integer, String, JSON, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# --- TABLE 1: RAW DATA (The "Source of Truth") ---
class RawContract(Base):
    __tablename__ = "raw_contracts"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    full_pdf_text = Column(Text)  # Stores the entire PDF text
    upload_date = Column(String)

    # Relationship
    sla_report = relationship("SLAReport", back_populates="raw_contract", uselist=False)


# --- TABLE 2: SLA REPORT (Specific Fields + JSON) ---
class SLAReport(Base):
    __tablename__ = "sla_reports"

    id = Column(Integer, primary_key=True, index=True)
    raw_contract_id = Column(Integer, ForeignKey("raw_contracts.id"))
    
    # 1. Identity Fields
    vin_number = Column(String, index=True)
    vehicle_make = Column(String)
    vehicle_model = Column(String)
    vehicle_year = Column(Integer)  # e.g., 2025

    # 2. Financials (Float for math)
    interest_rate_apr = Column(Float)
    lease_term_months = Column(Integer)
    monthly_payment = Column(Float)
    down_payment = Column(Float)
    residual_value = Column(Float)
    buyout_price = Column(Float)

    # 3. Text Clauses (String for descriptions)
    mileage_allowance = Column(String)
    mileage_overage_charge = Column(String)
    early_termination_fee = Column(String)
    maintenance_responsibilities = Column(String)
    warranty_coverage = Column(String)
    insurance_requirements = Column(String)
    late_fee_policy = Column(String)
    recalls_text = Column(Text)

    # 4. JSON Backup (Contains everything)
    extracted_data = Column(JSON) 

    # 5. Validation Result
    gov_validation_status = Column(JSON)

    negotiation_points = Column(JSON)

    # Relationship
    raw_contract = relationship("RawContract", back_populates="sla_report")
