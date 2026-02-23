from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class MarketAnalysisRequest(BaseModel):
    contract_id: int = Field(..., description="Contract document ID")


class FairnessFactors(BaseModel):
    price_score: float = Field(..., description="Price fairness score (0-100)")
    apr_score: float = Field(..., description="APR fairness score (0-100)")
    fees_score: float = Field(..., description="Fees fairness score (0-100)")
    term_score: float = Field(..., description="Lease term fairness score (0-100)")


class CostBreakdown(BaseModel):
    vehicle_price: float = Field(..., description="Base vehicle price")
    interest_cost: float = Field(..., description="Total interest cost over lease term")
    fees: float = Field(..., description="Total fees")
    down_payment: float = Field(..., description="Down payment amount")


class MarketPriceData(BaseModel):
    market_average: float = Field(..., description="Average market price from listings")
    market_median: float = Field(..., description="Median market price from listings")
    lowest_listing: float = Field(..., description="Lowest listing price found")
    highest_listing: float = Field(..., description="Highest listing price found")
    typical_range_low: float = Field(..., description="Typical price range low end")
    typical_range_high: float = Field(..., description="Typical price range high end")
    listing_count: int = Field(0, description="Number of listings found")
    msrp: Optional[float] = Field(None, description="Manufacturer's Suggested Retail Price")


class MarketAnalysisResponse(BaseModel):
    contract_price: float = Field(..., description="Contract/Dealer's quoted price")
    market_price_data: MarketPriceData = Field(..., description="Market price data from APIs")
    expected_monthly_payment: float = Field(..., description="Expected monthly payment based on market")
    contract_monthly_payment: float = Field(..., description="Actual contract monthly payment")
    cost_breakdown: CostBreakdown = Field(..., description="Detailed cost breakdown")
    fairness_score: float = Field(..., description="Overall contract fairness score (0-100)")
    fairness_factors: FairnessFactors = Field(..., description="Individual fairness factor scores")
    vehicle_info: Optional[Dict] = Field(None, description="Vehicle information for reference")
    data_sources: List[str] = Field(default_factory=list, description="APIs used for data")
    currency: str = Field("USD", description="Currency code (USD, INR, EUR, etc.)")
    currency_symbol: str = Field("$", description="Currency symbol for display")
