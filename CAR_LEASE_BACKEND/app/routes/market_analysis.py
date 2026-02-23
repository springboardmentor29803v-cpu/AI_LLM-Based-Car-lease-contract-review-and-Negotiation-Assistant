"""Market Analysis API routes."""
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from database import SessionLocal
from app.services.market_service import MarketAnalysisService
from app.models.market_analysis import MarketAnalysisRequest, MarketAnalysisResponse

router = APIRouter()

# Initialize market analysis service
market_analysis_service = MarketAnalysisService()


@router.post("/market-analysis", response_model=MarketAnalysisResponse)
async def analyze_market(request: MarketAnalysisRequest):
    """
    Perform market analysis on an existing contract.
    
    This endpoint:
    1. Fetches combined_data from DB by contract_id
    2. Extracts vehicle info (make, model, year)
    3. Calls external APIs (MarketCheck, Auto.dev, CarQuery)
    4. Calculates expected monthly payment using EMI formula
    5. Computes fairness score based on multiple factors
    
    Args:
        request: MarketAnalysisRequest with contract_id
        
    Returns:
        MarketAnalysisResponse with market prices, payments, cost breakdown, and fairness score
    """
    db = SessionLocal()
    try:
        # Fetch contract from database
        result = db.execute(
            text("SELECT combined_data FROM contracts WHERE id = :contract_id"),
            {"contract_id": request.contract_id}
        ).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail=f"Contract with ID {request.contract_id} not found"
            )
        
        combined_data = result[0]
        
        if not combined_data:
            raise HTTPException(
                status_code=400,
                detail="Contract has no analyzed data. Please upload and process the contract first."
            )
        
        # Check if we have the necessary data
        vehicle = combined_data.get("vehicle", {})
        sla = combined_data.get("sla", {})
        
        if not vehicle or "error" in vehicle:
            raise HTTPException(
                status_code=400,
                detail="Vehicle data not available for this contract."
            )
        
        if not sla or "error" in sla:
            raise HTTPException(
                status_code=400,
                detail="SLA data not available for this contract."
            )
        
        # Perform market analysis
        analysis_result = market_analysis_service.analyze_contract(combined_data)
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Market analysis failed: {str(e)}"
        )
    finally:
        db.close()
