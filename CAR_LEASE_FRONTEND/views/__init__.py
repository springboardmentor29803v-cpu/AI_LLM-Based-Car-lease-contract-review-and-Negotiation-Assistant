"""Views module for ContractCoach pages."""
from .dashboard import render_dashboard
from .contract_analysis import render_contract_analysis
from .vin_lookup import render_vin_lookup
from .chat_assistant import render_chat_assistant
from .market_analysis import render_market_analysis

__all__ = [
    "render_dashboard",
    "render_contract_analysis",
    "render_vin_lookup",
    "render_chat_assistant",
    "render_market_analysis"
]
