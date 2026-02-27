# app/database.py - FIXED VERSION
# app/database.py

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "postgresql://postgres:123456pg@localhost:5432/car_contract_ai_v2"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ---------- DB Dependency ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- CONTRACT TABLE ----------
class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String)
    file_path = Column(String)
    raw_text = Column(Text)

    dealer_price = Column(Float, nullable=True)

    vin = Column(String)
    apr = Column(Float, nullable=True)
    lease_term_months = Column(Integer, nullable=True)
    monthly_payment = Column(Float, nullable=True)
    down_payment = Column(Float, nullable=True)
    mileage_allowance = Column(Integer, nullable=True)

    vehicle_make = Column(String)
    vehicle_model = Column(String)
    vehicle_year = Column(Integer)

    status = Column(String, default="uploaded")
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    file_size = Column(Integer)
    file_type = Column(String)


# ---------- NEGOTIATION RULE ----------
class NegotiationRule(Base):
    __tablename__ = "negotiation_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String, unique=True)
    field = Column(String)
    condition = Column(String)
    severity = Column(String)
    intent = Column(String)
    suggestion = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------- NEGOTIATION INTENT ----------
class NegotiationIntent(Base):
    __tablename__ = "negotiation_intents"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer)
    intent_name = Column(String)
    priority = Column(String)
    triggered_by = Column(String)
    description = Column(Text)
    action_items = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------- CHAT ----------
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, index=True)
    session_id = Column(String(100), index=True)
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


# ---------- INIT ----------
def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")