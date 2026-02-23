"""
Rules caching manager.

Loads pre-processed cleaned rules from cleaned_rules.json file.
Rules are cached for reuse across the application.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Global cache for cleaned rules
_CLEANED_RULES_CACHE: Optional[Dict[str, Any]] = None

# Path to the cleaned rules file
CLEANED_RULES_FILE = Path(__file__).parent.parent.parent / "cleaned_rules.json"


def initialize_rules_cache() -> Dict[str, Any]:
    """
    Load cleaned rules from file at application startup.
    
    This should be called once during app startup, not on every request.
    
    Returns:
        Cleaned and standardized rules
    """
    global _CLEANED_RULES_CACHE
    
    try:
        logger.info("Loading cleaned rules from file...")
        
        if not CLEANED_RULES_FILE.exists():
            raise FileNotFoundError(
                f"Cleaned rules file not found: {CLEANED_RULES_FILE}. "
                "Please ensure cleaned_rules.json exists in the CAR_LEASE_BACKEND directory."
            )
        
        with open(CLEANED_RULES_FILE, 'r') as f:
            _CLEANED_RULES_CACHE = json.load(f)
        
        fields_count = len(_CLEANED_RULES_CACHE.get('fields', []))
        scenarios_count = sum(
            len(f.get('scenarios', [])) 
            for f in _CLEANED_RULES_CACHE.get('fields', [])
        )
        
        logger.info(f"✓ Rules loaded: {fields_count} fields, {scenarios_count} scenarios")
        
        return _CLEANED_RULES_CACHE
        
    except Exception as e:
        logger.error(f"Failed to load rules cache: {e}")
        raise


def get_cached_rules() -> Dict[str, Any]:
    """
    Get cached cleaned rules.
    
    Must call initialize_rules_cache() first at startup.
    
    Returns:
        Cleaned and standardized rules
        
    Raises:
        RuntimeError: If rules not initialized
    """
    global _CLEANED_RULES_CACHE
    
    if _CLEANED_RULES_CACHE is None:
        raise RuntimeError(
            "Rules cache not initialized. Call initialize_rules_cache() at startup."
        )
    
    return _CLEANED_RULES_CACHE


def reload_rules() -> Dict[str, Any]:
    """
    Reload rules from file (useful for hot-reloading).
    
    Returns:
        Updated rules dictionary
    """
    global _CLEANED_RULES_CACHE
    _CLEANED_RULES_CACHE = None
    return initialize_rules_cache()
