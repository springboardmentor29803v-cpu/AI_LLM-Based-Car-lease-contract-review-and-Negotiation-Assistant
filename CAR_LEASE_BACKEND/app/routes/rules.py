"""
API endpoints for Rule Processing and Issue Detection.

Provides endpoints to:
1. Upload and process rules
2. Process contract data against rules
3. Detect issues and get negotiation intents
"""

import json
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.services.rule_processor import RuleProcessor
from app.services.rules_cache import get_cached_rules

router = APIRouter()

# Initialize the rule processor (used for detection and conversion)
rule_processor = RuleProcessor()

# ============================================================================
# PYDANTIC MODELS FOR API
# ============================================================================

class ScenarioResponse(BaseModel):
    """Cleaned scenario response model."""
    condition: str
    condition_type: str
    severity: str
    issue: str
    negotiation_intent: Optional[str] = None
    reason: Optional[str] = None
    regex_patterns: Optional[List[str]] = None
    numeric_value: Optional[float] = None
    numeric_range: Optional[tuple] = None


class FieldRuleResponse(BaseModel):
    """Cleaned field rule response model."""
    field: str
    field_type: str
    unit: Optional[str]
    normalized_unit: Optional[str]
    scenarios: List[ScenarioResponse]


class ProcessRulesResponse(BaseModel):
    """Response from rule processing."""
    rules_version: str
    applies_to: str
    processed_at: str
    fields: List[FieldRuleResponse]
    standards: Dict[str, Any]


class DetectedIssue(BaseModel):
    """A detected issue in contract data."""
    field: str = Field(..., description="Field name from SLA")
    severity: str = Field(..., description="Issue severity (none, low, medium, high)")
    issue: str = Field(..., description="Description of the issue")
    negotiation_intent: Optional[str] = Field(
        None, description="Recommended negotiation action"
    )
    reason: Optional[str] = Field(None, description="Reason for the issue")
    value: Any = Field(None, description="Actual value from contract")


class IssueDetectionRequest(BaseModel):
    """Request to detect issues in contract data."""
    contract_data: Dict[str, Any] = Field(
        ..., description="Extracted SLA data from contract"
    )


class IssueDetectionResponse(BaseModel):
    """Response from issue detection."""
    total_issues: int
    high_severity: int
    medium_severity: int
    low_severity: int
    issues: List[DetectedIssue]
    summary: str


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/rules/process", response_model=Dict[str, Any])
async def process_rules(rules_json: Dict[str, Any]):
    """
    Process and normalize messy rules JSON.

    Takes rules with inconsistent formatting and normalizes them into
    a clean, standardized format for issue detection.

    **Input Format:**
    - Conditions may be missing, improperly formatted, or natural language
    - Units may be mixed (%, currency, months)
    - Regex patterns may be incomplete
    - Severity and intent text may be inconsistent

    **Output Format:**
    - Standardized field names
    - Normalized units (%, months, USD, etc.)
    - Parsed conditions with types
    - Consistent severity levels
    - Filled negotiation intents

    **Example Request:**
    ```json
    {
      "rules_version": "1.2",
      "applies_to": "Car Lease SLA",
      "fields": [
        {
          "field": "apr",
          "type": "numeric",
          "unit": "%",
          "scenarios": [
            {
              "condition": ">8",
              "severity": "high",
              "issue": "High APR",
              "negotiation_intent": "Negotiate lower APR"
            }
          ]
        }
      ]
    }
    ```
    """
    try:
        cleaned_rules = rule_processor.process_rules(rules_json)
        return {
            "success": True,
            "rules": cleaned_rules
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing rules: {str(e)}"
        )


@router.post("/rules/process-file", response_model=Dict[str, Any])
async def process_rules_file(file: UploadFile = File(...)):
    """
    Upload and process rules from a JSON file.

    Accepts a JSON file containing messy rules and returns cleaned,
    standardized rules ready for issue detection.
    """
    try:
        contents = await file.read()
        rules_json = json.loads(contents.decode("utf-8"))
        cleaned_rules = rule_processor.process_rules(rules_json)

        return {
            "success": True,
            "filename": file.filename,
            "rules": cleaned_rules
        }
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON file"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing rules file: {str(e)}"
        )


@router.post("/issues/detect", response_model=IssueDetectionResponse)
async def detect_issues(request: IssueDetectionRequest,
                       rules: Optional[Dict[str, Any]] = None):
    """
    Detect issues in contract data using processed rules.

    Takes extracted SLA data from a contract and compares against
    standardized rules to identify issues and suggest negotiations.

    **Input:**
    - `contract_data`: Extracted SLA fields from contract
    - `rules`: Optional cleaned rules (uses cached rules if not provided)

    **Output:**
    - List of detected issues with severity and negotiation intents
    - Count of issues by severity level
    - Summary of key concerns

    **Example Request:**
    ```json
    {
      "contract_data": {
        "apr": "9.5%",
        "lease_term_months": "72",
        "monthly_payment": "$1200"
      }
    }
    ```

    **Example Response:**
    ```json
    {
      "total_issues": 2,
      "high_severity": 1,
      "medium_severity": 1,
      "low_severity": 0,
      "issues": [
        {
          "field": "apr",
          "severity": "high",
          "issue": "High APR",
          "negotiation_intent": "Negotiate lower APR"
        }
      ],
      "summary": "1 critical issues requiring immediate negotiation"
    }
    ```
    """
    try:
        # Use cached rules if not provided
        if rules is None:
            rules = get_cached_rules()

        # Detect issues
        detected_issues = rule_processor.detect_issues(
            request.contract_data, rules
        )

        # Count issues by severity
        severity_counts = {
            "high": sum(1 for i in detected_issues if i["severity"] == "high"),
            "medium": sum(1 for i in detected_issues if i["severity"] == "medium"),
            "low": sum(1 for i in detected_issues if i["severity"] == "low"),
        }

        # Generate summary
        if severity_counts["high"] > 0:
            summary = f"{severity_counts['high']} critical issues requiring immediate negotiation"
        elif severity_counts["medium"] > 0:
            summary = f"{severity_counts['medium']} moderate issues to address"
        else:
            summary = "No significant issues detected"

        # Convert to response objects
        issue_responses = [
            DetectedIssue(**issue) for issue in detected_issues
        ]

        return IssueDetectionResponse(
            total_issues=len(detected_issues),
            high_severity=severity_counts["high"],
            medium_severity=severity_counts["medium"],
            low_severity=severity_counts["low"],
            issues=issue_responses,
            summary=summary
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error detecting issues: {str(e)}"
        )


@router.post("/rules/validate", response_model=Dict[str, Any])
async def validate_rules(rules_json: Dict[str, Any]):
    """
    Validate rules structure without full processing.

    Checks if rules are properly formatted and identifies any structural issues.

    **Returns:**
    - Validation status (valid/invalid)
    - List of errors found (if any)
    - Warnings about potential issues
    - Validation summary
    """
    errors = []
    warnings = []

    try:
        # Check required fields
        if "fields" not in rules_json:
            errors.append("Missing 'fields' key in rules")
        else:
            fields = rules_json["fields"]
            if not isinstance(fields, list):
                errors.append("'fields' must be a list")
            else:
                for i, field in enumerate(fields):
                    if "field" not in field:
                        errors.append(f"Field {i}: missing 'field' name")
                    if "scenarios" not in field:
                        errors.append(f"Field {i}: missing 'scenarios'")
                    else:
                        for j, scenario in enumerate(field["scenarios"]):
                            if "condition" not in scenario:
                                warnings.append(
                                    f"Field {i}, Scenario {j}: missing 'condition'"
                                )
                            if "severity" not in scenario:
                                warnings.append(
                                    f"Field {i}, Scenario {j}: missing 'severity'"
                                )
                            if "negotiation_intent" not in scenario:
                                warnings.append(
                                    f"Field {i}, Scenario {j}: missing 'negotiation_intent'"
                                )

        is_valid = len(errors) == 0

        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "summary": f"{'✓ Valid' if is_valid else '✗ Invalid'} - {len(errors)} errors, {len(warnings)} warnings"
        }

    except Exception as e:
        return {
            "valid": False,
            "errors": [str(e)],
            "warnings": [],
            "summary": "Validation failed with exception"
        }


@router.get("/rules/standard-severities", response_model=Dict[str, str])
async def get_standard_severities():
    """
    Get list of standard severity levels.

    Returns the standardized severity values used throughout the system.
    """
    from app.services.rule_processor import Severity

    return {
        "severities": [
            {"value": s.value, "description": s.name}
            for s in Severity
        ],
        "default": "medium"
    }


@router.get("/rules/condition-types", response_model=Dict[str, str])
async def get_condition_types():
    """
    Get list of supported condition types.

    Returns the types of conditions that can be parsed and evaluated.
    """
    from app.services.rule_processor import ConditionType

    return {
        "types": [
            {"value": t.value, "description": t.name}
            for t in ConditionType
        ]
    }


@router.post("/converters/percentage", response_model=Dict[str, Any])
async def convert_percentage(value: str = Form(...)):
    """
    Convert a percentage string to decimal.

    Examples:
    - "8%" → 0.08
    - "8" → 0.08
    """
    result = rule_processor.converter.percentage_to_decimal(value)
    return {
        "input": value,
        "output": result,
        "status": "success" if result is not None else "failed"
    }


@router.post("/converters/currency", response_model=Dict[str, Any])
async def convert_currency(value: str = Form(...)):
    """
    Convert a currency string to numeric value.

    Examples:
    - "$1,500" → 1500
    - "₹1,50,000" → 150000
    """
    result = rule_processor.converter.currency_to_number(value)
    return {
        "input": value,
        "output": result,
        "status": "success" if result is not None else "failed"
    }


@router.post("/conditions/parse", response_model=Dict[str, Any])
async def parse_condition(condition: str = Form(...)):
    """
    Parse a condition string into structured format.

    Examples:
    - "missing" → type: missing
    - ">8" → type: numeric, operator: >, value: 8
    - "12-48" → type: range, min: 12, max: 48
    - "regex:pattern" → type: regex, pattern: pattern
    """
    cond_type, cond_data = rule_processor.parser.parse(condition)
    return {
        "input": condition,
        "type": cond_type.value,
        "data": cond_data,
        "status": "success" if cond_type.value != "unknown" else "unknown"
    }


@router.post("/conditions/evaluate", response_model=Dict[str, Any])
async def evaluate_condition(condition: str = Form(...),
                            value: float = Form(...)):
    """
    Evaluate if a value matches a numeric condition.

    Examples:
    - condition: ">8", value: 9 → matches: true
    - condition: "12-48", value: 50 → matches: false
    """
    cond_type, cond_data = rule_processor.parser.parse(condition)
    matches = rule_processor.parser.evaluate_numeric_condition(
        cond_type, cond_data, value
    )
    return {
        "condition": condition,
        "value": value,
        "condition_type": cond_type.value,
        "matches": matches
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check for rule processing service."""
    return {
        "status": "healthy",
        "service": "Rule Processing Layer",
        "version": "1.0.0"
    }
