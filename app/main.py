#C:\Users\Hi\Desktop\car-contract-ai-v2\app\main.py
# app/main.py
from fastapi import FastAPI
from app.database import init_db
from app.routes import upload, analyze, market_price,contracts,vin,negotiation


app = FastAPI(title="Car Contract AI")

# Initialize DB tables
init_db()

# Include routes
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(contracts.router, prefix="/api/v1", tags=["contracts"])
app.include_router(vin.router, prefix="/api/v1", tags=["vin Intelligence"])
app.include_router(market_price.router, prefix="/api/v1", tags=["Market Price"])
app.include_router(negotiation.router, prefix="/api/v1", tags=["Negotiation AI"])


@app.get("/")
def root():
    return {"message": "Car Contract AI Backend Running 🚗"}