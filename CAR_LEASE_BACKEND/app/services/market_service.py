"""
Market Analysis Service with MarketCheck API Integration.

Uses real MarketCheck API for market pricing data.
No simulated/random pricing - all data from API or contract values.
"""

import logging
import os
import re
import requests
from typing import Dict, Optional, Tuple, List
from app.models.market_analysis import (
    MarketAnalysisResponse,
    MarketPriceData,
    CostBreakdown,
    FairnessFactors
)

logger = logging.getLogger(__name__)

# MarketCheck API Cache - keyed by contract_id
_market_cache: Dict[int, Dict] = {}


class MarketAnalysisService:
    """Service for market analysis using MarketCheck API."""

    # MarketCheck API configuration - loaded from environment variables
    MARKETCHECK_BASE_URL = "https://api.marketcheck.com/v2"
    API_TIMEOUT = 8  # seconds

    def __init__(self):
        self.api_key = os.getenv("MARKETCHECK_API_KEY", "")
        self.api_secret = os.getenv("MARKETCHECK_API_SECRET", "")

    def _detect_currency(self, sla: Dict) -> Tuple[str, str]:
        """Detect currency from SLA data. Returns (currency_code, currency_symbol)."""
        fields_to_check = [
            sla.get("monthly_payment", ""),
            sla.get("down_payment", ""),
            sla.get("residual_value", ""),
            sla.get("cap_cost", ""),
            sla.get("msrp", "")
        ]
        
        for value in fields_to_check:
            if not isinstance(value, str):
                continue
            
            if '₹' in value:
                return ("INR", "₹")
            
            value_lower = value.lower()
            if re.search(r'\brs\.?\b|\binr\b', value_lower):
                return ("INR", "₹")
            if '€' in value or re.search(r'\beur\b', value_lower):
                return ("EUR", "€")
            if '£' in value or re.search(r'\bgbp\b', value_lower):
                return ("GBP", "£")
            if '$' in value or re.search(r'\busd\b', value_lower):
                return ("USD", "$")
        
        return ("USD", "$")

    def _parse_numeric(self, value: Optional[str]) -> float:
        """Parse numeric value from string, handling currency symbols and formats."""
        if not value:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if not isinstance(value, str):
            return 0.0

        # Remove currency symbols - handle various encodings including mojibake
        cleaned = value.strip()
        
        # Remove all currency symbols including unicode variants and encoding issues
        # The ₹ symbol can appear as various encoding artifacts
        cleaned = re.sub(r'[\u20b9\ufffd]', '', cleaned)  # Unicode rupee and replacement char
        cleaned = re.sub(r'(Rs\.?|INR|rs|\$|USD|EUR|€|£|\\u20b9)', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*(per\s+(month|annum|year)|monthly|annually).*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*(months?|days?|years?)\s*$', '', cleaned, flags=re.IGNORECASE)
        
        # Handle complex strings - extract first number
        if ':' in cleaned or ';' in cleaned:
            match = re.search(r'[\d,]+\.?\d*', cleaned)
            if match:
                cleaned = match.group(0)
            else:
                return 0.0
        
        # Remove ALL non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', cleaned)
        
        if not cleaned:
            return 0.0
        
        try:
            return float(cleaned)
        except ValueError:
            logger.warning(f"Could not parse numeric value: {value}")
            return 0.0

    def _calculate_dealer_price(self, sla: Dict) -> float:
        """
        Calculate dealer price using priority logic:
        1. If cap_cost exists -> dealer_price = cap_cost
        2. Else if msrp exists -> dealer_price = msrp * 0.92
        3. Else -> dealer_price = residual_value + (monthly_payment * term_months)
        """
        # Priority 1: Cap Cost
        cap_cost = self._parse_numeric(sla.get("cap_cost"))
        if cap_cost > 0:
            logger.info(f"Dealer price from cap_cost: {cap_cost}")
            return cap_cost
        
        # Priority 2: MSRP * 0.92
        msrp = self._parse_numeric(sla.get("msrp"))
        if msrp > 0:
            dealer_price = msrp * 0.92
            logger.info(f"Dealer price from MSRP ({msrp}): {dealer_price}")
            return dealer_price
        
        # Priority 3: Residual + (Monthly * Term)
        residual_value = self._parse_numeric(sla.get("residual_value"))
        monthly_payment = self._parse_numeric(sla.get("monthly_payment"))
        lease_term = self._parse_numeric(sla.get("lease_term_months"))
        
        if lease_term <= 0:
            lease_term = 36  # Default
        
        if residual_value > 0 and monthly_payment > 0:
            dealer_price = residual_value + (monthly_payment * lease_term)
            logger.info(f"Dealer price from residual + payments: {dealer_price}")
            return dealer_price
        
        # Fallback: estimate from payments
        down_payment = self._parse_numeric(sla.get("down_payment"))
        if monthly_payment > 0:
            total_payments = (monthly_payment * lease_term) + down_payment
            dealer_price = total_payments / 0.85  # Assume 85% of value paid over lease
            logger.info(f"Dealer price from payment estimate: {dealer_price}")
            return dealer_price
        
        return 0.0

    def _fetch_marketcheck_listings(self, make: str, model: str, year: str) -> Dict:
        """
        Fetch active vehicle listings from MarketCheck API.
        GET https://api.marketcheck.com/v2/search/car/active
        """
        try:
            url = f"{self.MARKETCHECK_BASE_URL}/search/car/active"
            params = {
                "api_key": self.api_key,
                "make": make,
                "model": model,
                "year": year,
                "rows": 50,
                "sort_by": "price",
                "sort_order": "asc"
            }
            
            response = requests.get(url, params=params, timeout=self.API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                listings = data.get("listings", [])
                prices = [float(l["price"]) for l in listings if l.get("price") and l["price"] > 0]
                
                if prices:
                    logger.info(f"MarketCheck listings: Found {len(prices)} prices for {year} {make} {model}")
                    return {
                        "success": True,
                        "prices": prices,
                        "count": len(prices),
                        "source": "MarketCheck Listings"
                    }
                else:
                    logger.info(f"MarketCheck listings: No prices found for {year} {make} {model}")
            else:
                logger.warning(f"MarketCheck listings API returned status {response.status_code}: {response.text[:200] if response.text else 'No body'}")
                
        except requests.exceptions.Timeout:
            logger.warning("MarketCheck listings API timeout")
        except requests.exceptions.RequestException as e:
            logger.warning(f"MarketCheck listings API error: {e}")
        except Exception as e:
            logger.warning(f"MarketCheck listings processing error: {e}")
        
        return {"success": False, "prices": [], "count": 0, "source": None}

    def _fetch_marketcheck_predicted_price(self, make: str, model: str, year: str, mileage: int = 50000, trim: str = "") -> Dict:
        """
        Fetch predicted market price from MarketCheck API.
        GET https://api.marketcheck.com/v2/predict/car/price
        Requires: year, make, model, trim, miles, car_type
        """
        try:
            url = f"{self.MARKETCHECK_BASE_URL}/predict/car/price"
            params = {
                "api_key": self.api_key,
                "make": make,
                "model": model,
                "year": year,
                "miles": mileage,
                "car_type": "used",
                "trim": trim if trim else "Base"  # Default to Base if not specified
            }
            
            response = requests.get(url, params=params, timeout=self.API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                predicted_price = data.get("predicted_price") or data.get("price")
                
                if predicted_price and predicted_price > 0:
                    logger.info(f"MarketCheck predicted price: ${predicted_price} for {year} {make} {model}")
                    return {
                        "success": True,
                        "predicted_price": float(predicted_price),
                        "source": "MarketCheck Price Prediction"
                    }
            else:
                logger.warning(f"MarketCheck predict API returned status {response.status_code}: {response.text[:200] if response.text else 'No body'}")
                
        except requests.exceptions.Timeout:
            logger.warning("MarketCheck predict API timeout")
        except requests.exceptions.RequestException as e:
            logger.warning(f"MarketCheck predict API error: {e}")
        except Exception as e:
            logger.warning(f"MarketCheck predict processing error: {e}")
        
        return {"success": False, "predicted_price": None, "source": None}

    def _fetch_marketcheck_analytics(self, make: str, model: str, year: str) -> Dict:
        """
        Fetch market analytics from MarketCheck API.
        GET https://api.marketcheck.com/v2/predict/car/us/marketcheck_price
        """
        try:
            url = f"{self.MARKETCHECK_BASE_URL}/predict/car/us/marketcheck_price"
            params = {
                "api_key": self.api_key,
                "make": make,
                "model": model,
                "year": year
            }
            
            response = requests.get(url, params=params, timeout=self.API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract analytics values
                market_avg = data.get("average_price") or data.get("avg_price") or data.get("price")
                market_low = data.get("low_price") or data.get("min_price")
                market_high = data.get("high_price") or data.get("max_price")
                
                if market_avg and market_avg > 0:
                    logger.info(f"MarketCheck analytics: avg=${market_avg}, low=${market_low}, high=${market_high}")
                    return {
                        "success": True,
                        "market_avg_price": float(market_avg) if market_avg else None,
                        "market_low_price": float(market_low) if market_low else None,
                        "market_high_price": float(market_high) if market_high else None,
                        "source": "MarketCheck Analytics"
                    }
            else:
                logger.warning(f"MarketCheck analytics API returned status {response.status_code}: {response.text[:200] if response.text else 'No body'}")
                
        except requests.exceptions.Timeout:
            logger.warning("MarketCheck analytics API timeout")
        except requests.exceptions.RequestException as e:
            logger.warning(f"MarketCheck analytics API error: {e}")
        except Exception as e:
            logger.warning(f"MarketCheck analytics processing error: {e}")
        
        return {"success": False, "market_avg_price": None, "market_low_price": None, "market_high_price": None, "source": None}

    def _get_market_data(self, make: str, model: str, year: str) -> Tuple[MarketPriceData, List[str]]:
        """
        Aggregate market data from MarketCheck APIs.
        Uses all three endpoints and combines results.
        Returns (MarketPriceData, list of data sources used).
        """
        data_sources = []
        prices = []
        market_avg = None
        market_low = None
        market_high = None
        predicted_price = None
        
        # 1. Fetch listings
        listings_result = self._fetch_marketcheck_listings(make, model, year)
        if listings_result["success"]:
            prices = listings_result["prices"]
            data_sources.append(listings_result["source"])
        
        # 2. Fetch predicted price
        predict_result = self._fetch_marketcheck_predicted_price(make, model, year)
        if predict_result["success"]:
            predicted_price = predict_result["predicted_price"]
            if predict_result["source"]:
                data_sources.append(predict_result["source"])
        
        # Note: Market Analytics endpoint skipped - requires location data (zip/city)
        # We use listings + price prediction instead which work without location
        
        # Calculate market data from best available sources
        if prices:
            # Use actual listing data
            import statistics
            prices.sort()
            
            calc_avg = statistics.mean(prices) if not market_avg else market_avg
            calc_median = statistics.median(prices)
            calc_low = min(prices) if not market_low else market_low
            calc_high = max(prices) if not market_high else market_high
            
            # Typical range: 10th to 90th percentile
            n = len(prices)
            low_idx = max(0, int(n * 0.1))
            high_idx = min(n - 1, int(n * 0.9))
            typical_low = prices[low_idx]
            typical_high = prices[high_idx]
            
            market_price_data = MarketPriceData(
                market_average=round(calc_avg, 2),
                market_median=round(calc_median, 2),
                lowest_listing=round(calc_low, 2),
                highest_listing=round(calc_high, 2),
                typical_range_low=round(typical_low, 2),
                typical_range_high=round(typical_high, 2),
                listing_count=len(prices),
                msrp=None
            )
        elif market_avg:
            # Use analytics data only
            market_price_data = MarketPriceData(
                market_average=round(market_avg, 2),
                market_median=round(market_avg, 2),  # Use avg as median estimate
                lowest_listing=round(market_low, 2) if market_low else round(market_avg * 0.85, 2),
                highest_listing=round(market_high, 2) if market_high else round(market_avg * 1.15, 2),
                typical_range_low=round(market_low, 2) if market_low else round(market_avg * 0.90, 2),
                typical_range_high=round(market_high, 2) if market_high else round(market_avg * 1.10, 2),
                listing_count=0,
                msrp=None
            )
        elif predicted_price:
            # Use predicted price only
            market_price_data = MarketPriceData(
                market_average=round(predicted_price, 2),
                market_median=round(predicted_price, 2),
                lowest_listing=round(predicted_price * 0.85, 2),
                highest_listing=round(predicted_price * 1.15, 2),
                typical_range_low=round(predicted_price * 0.90, 2),
                typical_range_high=round(predicted_price * 1.10, 2),
                listing_count=0,
                msrp=None
            )
        else:
            # No market data available - will use dealer price as reference later
            logger.warning(f"No market data found for {year} {make} {model}")
            market_price_data = None
        
        return market_price_data, data_sources

    def _calculate_expected_monthly_payment(
        self,
        vehicle_price: float,
        down_payment: float,
        apr: float,
        lease_term_months: int
    ) -> float:
        """Calculate expected monthly payment using EMI formula."""
        if lease_term_months <= 0:
            return 0.0
        
        principal = vehicle_price - down_payment
        if principal <= 0:
            return 0.0
        
        if apr == 0:
            return round(principal / lease_term_months, 2)
        
        monthly_rate = apr / 12 / 100
        numerator = principal * monthly_rate * pow(1 + monthly_rate, lease_term_months)
        denominator = pow(1 + monthly_rate, lease_term_months) - 1
        
        return round(numerator / denominator, 2)

    def _calculate_cost_breakdown(
        self,
        vehicle_price: float,
        down_payment: float,
        monthly_payment: float,
        lease_term_months: int,
        fees_total: float = 0.0
    ) -> CostBreakdown:
        """Calculate detailed cost breakdown."""
        total_paid = (monthly_payment * lease_term_months) + down_payment
        interest_cost = max(0, total_paid - vehicle_price)
        
        return CostBreakdown(
            vehicle_price=round(vehicle_price, 2),
            interest_cost=round(interest_cost, 2),
            fees=round(fees_total, 2),
            down_payment=round(down_payment, 2)
        )

    def _calculate_fairness_score(
        self,
        dealer_price: float,
        market_average: float,
        apr: float,
        lease_term_months: int,
        fees_total: float
    ) -> Tuple[float, FairnessFactors]:
        """Calculate fairness score and individual factors."""
        price_score = 100.0
        apr_score = 100.0
        fees_score = 100.0
        term_score = 100.0
        
        # Price Score (40% weight) - compare dealer to market
        # More aggressive penalty for overpricing
        if market_average > 0:
            overpayment_pct = ((dealer_price - market_average) / market_average) * 100
            if overpayment_pct > 0:
                # Each 1% overpayment costs 3 points (max penalty at ~33% over)
                price_score = max(0, 100 - (overpayment_pct * 3))
            else:
                # Bonus for underpaying (max 10 bonus points)
                price_score = min(110, 100 + abs(overpayment_pct) * 0.5)
        
        # APR Score (25% weight)
        if apr > 10:
            apr_score = max(0, 100 - ((apr - 10) * 15))
        elif apr > 8:
            apr_score = max(0, 100 - ((apr - 8) * 10))
        elif apr > 6:
            apr_score = max(0, 100 - ((apr - 6) * 5))
        
        # Fees Score (15% weight)
        if fees_total > 0:
            if fees_total > 2000:
                fees_score = max(0, 100 - 30)
            elif fees_total > 1000:
                fees_score = max(0, 100 - 20)
            else:
                fees_score = max(0, 100 - 10)
        
        # Term Score (20% weight)
        if lease_term_months < 12:
            term_score = max(0, 100 - 30)
        elif lease_term_months > 72:
            term_score = max(0, 100 - 25)
        elif lease_term_months > 60:
            term_score = max(0, 100 - 10)
        
        # Weighted fairness score - price has highest weight
        fairness_score = (
            price_score * 0.40 +
            apr_score * 0.25 +
            fees_score * 0.15 +
            term_score * 0.20
        )
        
        return round(fairness_score, 2), FairnessFactors(
            price_score=round(price_score, 2),
            apr_score=round(apr_score, 2),
            fees_score=round(fees_score, 2),
            term_score=round(term_score, 2)
        )

    def analyze_contract(self, combined_data: Dict, contract_id: Optional[int] = None) -> MarketAnalysisResponse:
        """
        Perform market analysis on contract data.
        
        Args:
            combined_data: Contract data from database (combined_data JSONB field)
            contract_id: Optional contract ID for caching
            
        Returns:
            MarketAnalysisResponse with market analysis data
        """
        # Check cache first
        if contract_id and contract_id in _market_cache:
            logger.info(f"Using cached market data for contract {contract_id}")
            return _market_cache[contract_id]
        
        # Extract vehicle data
        vehicle = combined_data.get("vehicle", {})
        make = vehicle.get("Make", vehicle.get("make", "Unknown"))
        model = vehicle.get("Model", vehicle.get("model", "Unknown"))
        year = str(vehicle.get("ModelYear", vehicle.get("year", "Unknown")))
        
        # Extract SLA data
        sla = combined_data.get("sla", {})
        
        # Detect currency
        currency_code, currency_symbol = self._detect_currency(sla)
        logger.info(f"Detected currency: {currency_code} ({currency_symbol})")
        
        # Parse SLA values
        monthly_payment = self._parse_numeric(sla.get("monthly_payment"))
        down_payment = self._parse_numeric(sla.get("down_payment"))
        apr = self._parse_numeric(sla.get("apr"))
        lease_term_months = int(self._parse_numeric(sla.get("lease_term_months"))) or 36
        fees_total = self._parse_numeric(sla.get("fees_total"))
        
        # Calculate dealer price using priority logic
        dealer_price = self._calculate_dealer_price(sla)
        
        # Fetch market data from MarketCheck API
        market_price_data, data_sources = self._get_market_data(make, model, year)
        
        # If no market data and we have dealer price, create synthetic market data
        if market_price_data is None and dealer_price > 0:
            # Create market data based on dealer price for fair comparison
            logger.info(f"Creating synthetic market data from dealer price: {dealer_price}")
            market_price_data = MarketPriceData(
                market_average=round(dealer_price * 1.0, 2),  # Use dealer price as market average
                market_median=round(dealer_price * 1.0, 2),
                lowest_listing=round(dealer_price * 0.90, 2),
                highest_listing=round(dealer_price * 1.10, 2),
                typical_range_low=round(dealer_price * 0.92, 2),
                typical_range_high=round(dealer_price * 1.08, 2),
                listing_count=0,
                msrp=None
            )
            data_sources.append("Contract-Based Estimate")
        elif market_price_data is None:
            # No dealer price either - use placeholder
            market_price_data = MarketPriceData(
                market_average=0,
                market_median=0,
                lowest_listing=0,
                highest_listing=0,
                typical_range_low=0,
                typical_range_high=0,
                listing_count=0,
                msrp=None
            )
            data_sources.append("No Data Available")
        
        # Calculate expected monthly payment
        base_price = market_price_data.market_average if market_price_data.market_average > 0 else dealer_price
        expected_monthly = self._calculate_expected_monthly_payment(
            vehicle_price=base_price,
            down_payment=down_payment,
            apr=apr,
            lease_term_months=lease_term_months
        )
        
        # Calculate cost breakdown
        cost_breakdown = self._calculate_cost_breakdown(
            vehicle_price=dealer_price,
            down_payment=down_payment,
            monthly_payment=monthly_payment,
            lease_term_months=lease_term_months,
            fees_total=fees_total
        )
        
        # Calculate fairness score
        market_avg_for_score = market_price_data.market_average if market_price_data.market_average > 0 else dealer_price
        fairness_score, fairness_factors = self._calculate_fairness_score(
            dealer_price=dealer_price,
            market_average=market_avg_for_score,
            apr=apr,
            lease_term_months=lease_term_months,
            fees_total=fees_total
        )
        
        # Build response
        response = MarketAnalysisResponse(
            contract_price=round(dealer_price, 2),  # dealer_price as contract_price
            market_price_data=market_price_data,
            expected_monthly_payment=expected_monthly,
            contract_monthly_payment=round(monthly_payment, 2),
            cost_breakdown=cost_breakdown,
            fairness_score=fairness_score,
            fairness_factors=fairness_factors,
            vehicle_info={
                "make": make,
                "model": model,
                "year": year
            },
            data_sources=data_sources,
            currency=currency_code,
            currency_symbol=currency_symbol
        )
        
        # Cache the result
        if contract_id:
            _market_cache[contract_id] = response
            logger.info(f"Cached market data for contract {contract_id}")
        
        return response


def clear_market_cache(contract_id: Optional[int] = None):
    """Clear market data cache."""
    global _market_cache
    if contract_id:
        _market_cache.pop(contract_id, None)
        logger.info(f"Cleared market cache for contract {contract_id}")
    else:
        _market_cache = {}
        logger.info("Cleared all market cache")
