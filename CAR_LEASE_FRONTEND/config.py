"""Configuration settings for ContractCoach frontend."""

# Backend API configuration
API_BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/api/upload"
CHAT_ENDPOINT = f"{API_BASE_URL}/api/chat"
MARKET_ANALYSIS_ENDPOINT = f"{API_BASE_URL}/api/market-analysis"

# File upload settings
MAX_FILE_SIZE_MB = 10
ALLOWED_FILE_TYPES = ["pdf", "png", "jpg", "jpeg"]

# App settings
APP_NAME = "ContractCoach"
APP_ICON = "C"
COPYRIGHT_YEAR = 2026
