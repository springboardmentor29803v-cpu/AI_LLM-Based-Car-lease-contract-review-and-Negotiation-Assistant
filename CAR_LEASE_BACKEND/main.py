from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from app.routes.upload import router as upload_router
from app.routes.rules import router as rules_router
from app.routes.chat import router as chat_router
from app.routes.market_analysis import router as market_analysis_router
from app.services.rules_cache import initialize_rules_cache
from app.services.chat_service import initialize_chat_service

# Initialize FastAPI app
app = FastAPI(
    title="Car Lease Contract Review API",
    description="Backend for PDF upload, OCR extraction, contract analysis, and AI negotiation assistant",
    version="1.0.0"
)

# Configure CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Initialize database, rules cache, and chat service on application startup"""
    print("🚀 Starting Car Lease Backend...")
    init_db()
    print("✓ Database initialized")
    
    # Process rules ONCE at startup (not on every request)
    initialize_rules_cache()
    print("✓ Rules cache initialized")
    
    # Initialize chat service (creates chat database)
    initialize_chat_service()
    print("✓ Chat service initialized")

# Include routers
app.include_router(upload_router, prefix="/api", tags=["Upload"])
app.include_router(rules_router, prefix="/api", tags=["Rules"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(market_analysis_router, prefix="/api", tags=["Market Analysis"])

# Root endpoint
@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Car Lease Contract Review API",
        "version": "1.0.0"
    }

# Run with: uvicorn main:app --reload --port 8000
