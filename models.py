from sqlalchemy import Column, Integer, String, Text,JSON,DateTime, ForeignKey,Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import ContractBase,NegotiationBase
from sqlalchemy.sql import func
import datetime
import uuid

class Contract(ContractBase):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255))
    raw_text = Column(Text)
    apr = Column(Text, nullable=True)
    lease_term_months = Column(Text, nullable=True)
    monthly_payment = Column(Text, nullable=True)
    down_payment = Column(Text, nullable=True)
    residual_value = Column(Text, nullable=True)
    mileage_allowance = Column(Text, nullable=True)
    early_termination_clause= Column(Text, nullable=True)
    purchase_option=Column(Text, nullable=True)
    late_fees=Column(Text, nullable=True)
    
    vin = Column(Text, nullable=True)
    vehicle_make = Column(Text, nullable=True)
    vehicle_model = Column(Text, nullable=True)
    vehicle_year = Column(Text, nullable=True)
    vehicle_type = Column(Text, nullable=True)
    recalls = Column(JSON, nullable=True)

class ContractSLA(NegotiationBase):
    __tablename__ = "contract_sla"

    id = Column(Integer, primary_key=True, index=True)

    raw_text = Column(Text)  # ← ADD THIS (for LLM price extraction)
    vin = Column(String(17))  # ← ADD THIS (for MarketCheck)
    market_value_inr = Column(Float)  # ← ADD THIS
    price_difference = Column(Float)  # ← ADD THIS
    analysis_status = Column(String)
    
    contract_id = Column(Integer, index=True, nullable=True)

    apr_percent = Column(Float, nullable=True)
    money_factor = Column(Float, nullable=True)
    term_months = Column(Integer, nullable=True)
    monthly_payment = Column(Float, nullable=True)
    down_payment = Column(Float, nullable=True)
    fees_total = Column(Float, nullable=True)
    residual_value = Column(Float, nullable=True)
    residual_percent_msrp = Column(Float, nullable=True)
    msrp = Column(Float, nullable=True)
    cap_cost = Column(Float, nullable=True)
    cap_cost_reduction = Column(Float, nullable=True)
    mileage_allowance_yr = Column(Integer, nullable=True)
    mileage_overage_fee = Column(Float, nullable=True)
    early_termination_fee = Column(Float, nullable=True)
    disposition_fee = Column(Float, nullable=True)
    purchase_option_price = Column(Float, nullable=True)

    insurance_requirements = Column(Text, nullable=True)
    maintenance_resp = Column(Text, nullable=True)
    warranty_summary = Column(Text, nullable=True)
    late_fee_policy = Column(Text, nullable=True)
    other_terms = Column(Text, nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
    )
    
    mileage = Column(Integer, nullable=True)
    dealer_price_inr = Column(Float, nullable=True)
    market_price_usd = Column(Float, nullable=True)
    fairness_score = Column(Float, nullable=True)
    price_source = Column(String(50), nullable=True)

    price_score = Column(Float, nullable=True)
    apr_score = Column(Float, nullable=True)
    fees_score = Column(Float, nullable=True)
    term_score = Column(Float, nullable=True)

class NegotiationMessage(NegotiationBase):
    __tablename__ = "negotiation_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), index=True)

    sender_role = Column(String(16))  
    body = Column(Text)

    suggested_text = Column(Text, nullable=True)
    attachments = Column(JSONB, nullable=True)

    sent_at = Column(DateTime, default=datetime.datetime.utcnow)

class NegotiationThread(NegotiationBase):
    __tablename__ = "negotiation_threads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)      
    contract_id = Column(UUID(as_uuid=True), nullable=True)   
    dealer_id=Column(UUID(as_uuid=True), nullable=True) 
    lender_id = Column(UUID(as_uuid=True), nullable=True)    
    channel = Column(String, nullable=True)                  
    subject = Column(String, nullable=True)                  
      
    created_at = Column(DateTime, default=func.now())
    closed_at = Column(DateTime, nullable=True)              
    
    sla_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
