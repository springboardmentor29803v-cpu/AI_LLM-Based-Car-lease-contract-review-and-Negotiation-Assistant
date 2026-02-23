import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

# PostgreSQL connection URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable not set. "
        "Please configure it in .env file or as a system environment variable."
    )

# Create engine and session factory
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create contracts and chat_messages tables if not exists"""
    with engine.begin() as conn:
        # Create contracts table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS contracts (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                raw_text TEXT,
                sla_data JSONB,
                vehicle_data JSONB,
                combined_data JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            ALTER TABLE contracts
            ADD COLUMN IF NOT EXISTS sla_data JSONB
        """))
        conn.execute(text("""
            ALTER TABLE contracts
            ADD COLUMN IF NOT EXISTS vehicle_data JSONB
        """))
        conn.execute(text("""
            ALTER TABLE contracts
            ADD COLUMN IF NOT EXISTS combined_data JSONB
        """))
        
        # Add new financial columns for lease analysis
        conn.execute(text("""
            ALTER TABLE contracts
            ADD COLUMN IF NOT EXISTS cap_cost DECIMAL(12,2)
        """))
        conn.execute(text("""
            ALTER TABLE contracts
            ADD COLUMN IF NOT EXISTS msrp DECIMAL(12,2)
        """))
        conn.execute(text("""
            ALTER TABLE contracts
            ADD COLUMN IF NOT EXISTS cap_cost_reduction DECIMAL(12,2)
        """))
        conn.execute(text("""
            ALTER TABLE contracts
            ADD COLUMN IF NOT EXISTS fees_total DECIMAL(12,2)
        """))
        conn.execute(text("""
            ALTER TABLE contracts
            ADD COLUMN IF NOT EXISTS money_factor DECIMAL(10,6)
        """))
        conn.execute(text("""
            ALTER TABLE contracts
            ADD COLUMN IF NOT EXISTS purchase_option_price DECIMAL(12,2)
        """))
        
        # Create chat_messages table for chat history
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id SERIAL PRIMARY KEY,
                contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_chat_messages_contract_id 
            ON chat_messages(contract_id)
        """))
    print("✓ Database initialized: contracts and chat_messages tables ready")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
