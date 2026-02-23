"""
Rule Processing Layer for Contract Negotiation Assistant.

Handles normalization, parsing, validation, and evaluation of negotiation rules
from messy JSON into clean, standardized, actionable rule formats.
"""

import json
import re
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Severity(str, Enum):
    """Standard severity levels for identified issues."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ConditionType(str, Enum):
    """Types of conditions in rules."""
    MISSING = "missing"
    NUMERIC = "numeric"
    RANGE = "range"
    REGEX = "regex"
    UNKNOWN = "unknown"


@dataclass
class CleanedScenario:
    """Standardized scenario after processing."""
    condition: str
    condition_type: ConditionType
    severity: Severity
    issue: str
    negotiation_intent: Optional[str]
    reason: Optional[str] = None
    regex_patterns: Optional[List[str]] = None
    numeric_value: Optional[Union[int, float]] = None
    numeric_range: Optional[Tuple[Optional[float], Optional[float]]] = None


@dataclass
class CleanedRule:
    """Standardized rule after processing."""
    field: str
    field_type: str
    unit: Optional[str]
    normalized_unit: Optional[str]
    scenarios: List[CleanedScenario]


class PercentCurrencyConverter:
    """Converts percentages and currency values to standardized numeric format."""

    CURRENCY_SYMBOLS = {
        '$': 'USD',
        '₹': 'INR',
        '€': 'EUR',
        '£': 'GBP',
        '¥': 'JPY',
        '\ufffd': 'INR',  # Unicode replacement character (encoding issue)
    }

    @staticmethod
    def percentage_to_decimal(value: Union[str, int, float]) -> Optional[float]:
        """
        Convert percentage string to decimal.
        Examples: "8%" → 0.08, "8" → 0.08
        """
        if value is None:
            return None

        try:
            # Remove % symbol if present
            str_val = str(value).strip().rstrip('%')
            decimal = float(str_val) / 100
            return round(decimal, 4)
        except (ValueError, AttributeError):
            logger.warning(f"Cannot convert '{value}' to percentage decimal")
            return None

    @staticmethod
    def currency_to_number(value: str) -> Optional[float]:
        """
        Convert currency string to numeric value.
        Examples: "$1,500" → 1500, "₹1,50,000" → 150000
        """
        if not value or not isinstance(value, str):
            return None

        try:
            # Remove currency symbols and whitespace
            for symbol in PercentCurrencyConverter.CURRENCY_SYMBOLS.keys():
                value = value.replace(symbol, '')
            
            # Remove Unicode Rupee symbol and encoding artifacts
            value = re.sub(r'[\u20b9\ufffd]', '', value)

            # Remove commas and other separators
            value = re.sub(r'[^\d.]', '', value)

            if not value:
                return None

            return float(value)
        except (ValueError, AttributeError):
            logger.warning(f"Cannot convert to currency number")

        return None

    @staticmethod
    def normalize_unit(unit: Optional[str], value: Optional[Any] = None) -> Optional[str]:
        """
        Normalize unit names for consistency.
        """
        if not unit:
            return None

        unit_lower = unit.lower().strip()

        # Percentage variants
        if any(x in unit_lower for x in ['%', 'percent', 'pct']):
            return '%'

        # Currency variants
        if any(x in unit_lower for x in ['usd', 'dollar', '$', 'currency']):
            return 'USD'
        if any(x in unit_lower for x in ['inr', 'rupee', '₹', 'rs']):
            return 'INR'

        # Time variants
        if any(x in unit_lower for x in ['month', 'months']):
            return 'months'
        if any(x in unit_lower for x in ['year', 'years']):
            return 'years'

        # Distance variants
        if any(x in unit_lower for x in ['mile', 'miles', 'mi']):
            return 'miles'
        if any(x in unit_lower for x in ['km', 'kilometer']):
            return 'km'

        return unit_lower


class ConditionParser:
    """Parses condition strings into structured format."""

    # Regex patterns for different condition types
    MISSING_PATTERN = r'^missing$'
    NUMERIC_PATTERN = r'^(<=?|>=?|=)?\s*(\d+(?:\.\d+)?)\s*(%)?$'
    RANGE_PATTERN = r'^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$'
    COMPARISON_PATTERN = r'^(<=?|>=?)\s*(\d+(?:\.\d+)?)\s*(%)?$'
    REGEX_CONDITION_PATTERN = r'^regex:(.+)$'

    @staticmethod
    def parse(condition: str) -> Tuple[ConditionType, Dict[str, Any]]:
        """
        Parse a condition string and return type and structured data.

        Returns:
            Tuple of (ConditionType, parsed_data_dict)
        """
        if not condition:
            return ConditionType.UNKNOWN, {}

        condition = str(condition).strip().lower()

        # Check for missing
        if re.match(ConditionParser.MISSING_PATTERN, condition):
            return ConditionType.MISSING, {"value": None}

        # Check for regex pattern
        regex_match = re.match(ConditionParser.REGEX_CONDITION_PATTERN, condition)
        if regex_match:
            pattern = regex_match.group(1)
            return ConditionType.REGEX, {"pattern": pattern, "patterns": [pattern]}

        # Check for range (12-48)
        range_match = re.match(ConditionParser.RANGE_PATTERN, condition)
        if range_match:
            min_val = float(range_match.group(1))
            max_val = float(range_match.group(2))
            return ConditionType.RANGE, {
                "min": min_val,
                "max": max_val,
                "range": (min_val, max_val)
            }

        # Check for comparison with operator (>8, <=6, <12, etc.)
        comparison_match = re.match(ConditionParser.COMPARISON_PATTERN, condition)
        if comparison_match:
            operator = comparison_match.group(1).strip()
            value = float(comparison_match.group(2))
            is_percent = comparison_match.group(3) is not None

            return ConditionType.NUMERIC, {
                "operator": operator,
                "value": value,
                "is_percent": is_percent,
                "numeric_value": value
            }

        # Try to extract just a numeric value
        try:
            value = float(condition)
            return ConditionType.NUMERIC, {"value": value, "numeric_value": value}
        except ValueError:
            pass

        return ConditionType.UNKNOWN, {"raw": condition}

    @staticmethod
    def evaluate_numeric_condition(condition_type: ConditionType,
                                   condition_data: Dict[str, Any],
                                   value: Union[int, float]) -> bool:
        """
        Evaluate if a numeric value matches a parsed condition.

        Args:
            condition_type: Type of condition
            condition_data: Parsed condition data
            value: Value to test

        Returns:
            True if condition matches, False otherwise
        """
        if condition_type == ConditionType.MISSING:
            return value is None

        if condition_type == ConditionType.NUMERIC:
            operator = condition_data.get("operator", "=")
            threshold = condition_data.get("value")

            if operator == ">":
                return value > threshold
            elif operator == ">=":
                return value >= threshold
            elif operator == "<":
                return value < threshold
            elif operator == "<=":
                return value <= threshold
            elif operator == "=":
                return value == threshold
            else:
                return False

        if condition_type == ConditionType.RANGE:
            min_val = condition_data.get("min")
            max_val = condition_data.get("max")
            return min_val <= value <= max_val

        return False


class RegexEngine:
    """Compiles and manages regex patterns for clause detection."""

    # Predefined regex patterns for common clauses
    CLAUSE_PATTERNS = {
        "late_fees": [
            r"(late\s+fee|late\s+payment|overdue|delinquent)",
            r"(\d+%?\s+(?:per|per\s+month)|penalty|fine)",
        ],
        "early_termination": [
            r"(early\s+terminat|termination\s+fee|exit\s+fee|break\s+fee)",
            r"(remaining\s+balanc|early\s+termination)",
        ],
        "purchase_option": [
            r"(purchase\s+option|buyout|end\s+of\s+lease|residual)",
            r"(option\s+to\s+purchase|lease.*option)",
            r"(inspection\s+required|requires\s+inspection|vehicle\s+inspection)",
        ],
        "hidden_penalties": [
            r"(excess\s+wear|excess\s+mileag|gap\s+insurance|acquisition\s+fee)",
            r"(disposition\s+fee|documentation\s+fee|transfer\s+fee)",
        ],
        "apr_rate": [
            r"(apr|annual\s+percentage\s+rate|interest\s+rate)",
            r"(\d+(?:\.\d+)?%?\s+(?:per|per\s+annum|yearly))",
        ],
    }

    def __init__(self):
        """Initialize and compile all regex patterns."""
        self.compiled_patterns: Dict[str, List[re.Pattern]] = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile all patterns from CLAUSE_PATTERNS."""
        for clause, patterns in self.CLAUSE_PATTERNS.items():
            self.compiled_patterns[clause] = []
            for pattern in patterns:
                try:
                    compiled = re.compile(pattern, re.IGNORECASE)
                    self.compiled_patterns[clause].append(compiled)
                except re.error as e:
                    logger.error(f"Failed to compile regex for {clause}: {e}")

    def add_custom_pattern(self, clause_name: str, pattern: str):
        """Add a custom regex pattern for a clause."""
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
            if clause_name not in self.compiled_patterns:
                self.compiled_patterns[clause_name] = []
            self.compiled_patterns[clause_name].append(compiled)
        except re.error as e:
            logger.error(f"Failed to compile custom pattern for {clause_name}: {e}")

    def get_patterns(self, clause_name: str) -> List[str]:
        """Get raw patterns for a clause."""
        return self.CLAUSE_PATTERNS.get(clause_name, [])


class RegexEvaluator:
    """Evaluates regex conditions against SLA text fields."""

    def __init__(self, regex_engine: RegexEngine):
        """Initialize with a RegexEngine instance."""
        self.regex_engine = regex_engine

    def evaluate_text_field(self, field_value: str, patterns: List[str]) -> Tuple[bool, List[str]]:
        """
        Evaluate if text field matches any of the provided regex patterns.

        Args:
            field_value: Text to search
            patterns: List of regex patterns to test

        Returns:
            Tuple of (matched: bool, matches: list of matched text)
        """
        if not field_value or not isinstance(field_value, str):
            return False, []

        matched_texts = []
        for pattern_str in patterns:
            try:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                matches = pattern.findall(field_value)
                if matches:
                    matched_texts.extend(matches)
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern_str}': {e}")

        return len(matched_texts) > 0, list(set(matched_texts))

    def evaluate_clause(self, field_value: str, clause_name: str) -> Tuple[bool, List[str]]:
        """
        Evaluate if text field matches patterns for a specific clause.

        Args:
            field_value: Text to search
            clause_name: Name of clause (e.g., "late_fees", "early_termination")

        Returns:
            Tuple of (matched: bool, matches: list of matched text)
        """
        patterns = self.regex_engine.compiled_patterns.get(clause_name, [])
        if not patterns:
            return False, []

        matched_texts = []
        for pattern in patterns:
            matches = pattern.findall(field_value)
            if matches:
                matched_texts.extend(matches)

        return len(matched_texts) > 0, list(set(matched_texts))


class NormalizationEngine:
    """Normalizes and standardizes rule scenarios."""

    DEFAULT_SEVERITIES = {
        "missing": Severity.MEDIUM,
        "excellent": Severity.NONE,
        "good": Severity.LOW,
        "standard": Severity.NONE,
        "moderate": Severity.LOW,
        "high": Severity.HIGH,
        "excessive": Severity.HIGH,
        "restrictive": Severity.HIGH,
    }

    @staticmethod
    def normalize_severity(severity: Optional[str]) -> Severity:
        """
        Normalize severity string to standard Severity enum.

        If severity is missing or invalid, return MEDIUM as default.
        """
        if not severity:
            return Severity.MEDIUM

        severity_lower = str(severity).strip().lower()

        # Direct match
        try:
            return Severity(severity_lower)
        except ValueError:
            pass

        # Try to find by keyword
        for keyword, sev in NormalizationEngine.DEFAULT_SEVERITIES.items():
            if keyword in severity_lower:
                return sev

        return Severity.MEDIUM

    @staticmethod
    def normalize_negotiation_intent(intent: Optional[str],
                                     issue: Optional[str] = None) -> Optional[str]:
        """
        Normalize negotiation intent. If missing/null, provide sensible default.

        Args:
            intent: Original intent string
            issue: Issue description (used to generate default if needed)

        Returns:
            Normalized intent or None if severity is "none"
        """
        if intent and isinstance(intent, str) and intent.strip():
            return intent.strip()

        # Generate default based on issue
        if issue:
            issue_lower = issue.lower()
            if "missing" in issue_lower or "undefined" in issue_lower:
                return f"Clarify: {issue}"
            elif "high" in issue_lower or "excessive" in issue_lower:
                return f"Reduce: {issue}"
            elif "low" in issue_lower:
                return f"Increase: {issue}"

        return None

    @staticmethod
    def normalize_field_name(field: str) -> str:
        """Normalize field names to snake_case."""
        # Convert camelCase and spaces to snake_case
        field = re.sub(r'([A-Z])', r'_\1', field).lower()
        field = re.sub(r'[\s_]+', '_', field).strip('_')
        return field


class RuleProcessor:
    """
    Main orchestrator for rule processing.

    Coordinates all processing steps: normalization, parsing, validation, and evaluation.
    """

    def __init__(self):
        """Initialize all processing engines."""
        self.normalizer = NormalizationEngine()
        self.converter = PercentCurrencyConverter()
        self.parser = ConditionParser()
        self.regex_engine = RegexEngine()
        self.regex_evaluator = RegexEvaluator(self.regex_engine)

    def process_rules(self, rules_json: Union[str, Dict]) -> Dict[str, Any]:
        """
        Process complete rules JSON from messy input to clean output.

        Args:
            rules_json: Rules JSON (string or dict)

        Returns:
            Processed and cleaned rules dict
        """
        # Parse JSON if string
        if isinstance(rules_json, str):
            try:
                rules = json.loads(rules_json)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                return {"error": "Invalid JSON format", "rules": []}
        else:
            rules = rules_json

        # Process each field's rules
        processed_fields = []
        if "fields" in rules:
            for field_rule in rules["fields"]:
                processed_field = self._process_field_rule(field_rule)
                processed_fields.append(processed_field)

        # Return cleaned rules
        return {
            "rules_version": rules.get("rules_version", "1.0"),
            "applies_to": rules.get("applies_to", "Car Lease"),
            "processed_at": self._get_timestamp(),
            "fields": processed_fields,
            "standards": rules.get("standards", {})
        }

    def _process_field_rule(self, field_rule: Dict[str, Any]) -> CleanedRule:
        """Process a single field rule."""
        field_name = self.normalizer.normalize_field_name(
            field_rule.get("field", "unknown")
        )
        field_type = field_rule.get("type", "text")
        unit = field_rule.get("unit", None)
        normalized_unit = self.converter.normalize_unit(unit)

        # Process scenarios
        scenarios = []
        for scenario in field_rule.get("scenarios", []):
            processed_scenario = self._process_scenario(
                scenario, field_type, normalized_unit
            )
            scenarios.append(processed_scenario)

        return CleanedRule(
            field=field_name,
            field_type=field_type,
            unit=unit,
            normalized_unit=normalized_unit,
            scenarios=scenarios
        )

    def _process_scenario(self, scenario: Dict[str, Any],
                         field_type: str, normalized_unit: Optional[str]) -> CleanedScenario:
        """Process a single scenario within a field rule."""
        condition = scenario.get("condition", "")
        severity = self.normalizer.normalize_severity(scenario.get("severity"))
        issue = scenario.get("issue", "Unknown issue")
        reason = scenario.get("reason")
        intent = scenario.get("negotiation_intent")

        # Normalize negotiation intent
        normalized_intent = self.normalizer.normalize_negotiation_intent(intent, issue)

        # Parse condition
        condition_type, condition_data = self.parser.parse(condition)

        # Handle numeric conversions if applicable
        regex_patterns = None
        numeric_value = None
        numeric_range = None

        if condition_type == ConditionType.NUMERIC:
            numeric_value = condition_data.get("numeric_value")
            # Convert percentages to decimal if needed
            if condition_data.get("is_percent"):
                numeric_value = self.converter.percentage_to_decimal(numeric_value)

        elif condition_type == ConditionType.RANGE:
            min_val = condition_data.get("min")
            max_val = condition_data.get("max")
            # Convert percentages if applicable
            if normalized_unit == "%":
                min_val = self.converter.percentage_to_decimal(min_val)
                max_val = self.converter.percentage_to_decimal(max_val)
            numeric_range = (min_val, max_val)

        elif condition_type == ConditionType.REGEX:
            regex_patterns = condition_data.get("patterns", [])

        return CleanedScenario(
            condition=condition,
            condition_type=condition_type,
            severity=severity,
            issue=issue,
            negotiation_intent=normalized_intent,
            reason=reason,
            regex_patterns=regex_patterns,
            numeric_value=numeric_value,
            numeric_range=numeric_range
        )

    def detect_issues(self, sla_data: Dict[str, Any],
                     rules: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect issues in SLA data using processed rules.

        Args:
            sla_data: Extracted SLA data from contract
            rules: Processed rules

        Returns:
            List of detected issues with negotiation intents
        """
        issues = []

        for field_rule in rules.get("fields", []):
            field_name = field_rule["field"]
            field_value = sla_data.get(field_name)

            for scenario in field_rule.get("scenarios", []):
                matched = self._match_scenario(
                    field_value, scenario, field_rule.get("normalized_unit")
                )

                if matched:
                    issues.append({
                        "field": field_name,
                        "severity": scenario.get("severity", "medium"),
                        "issue": scenario.get("issue", "Unknown"),
                        "negotiation_intent": scenario.get("negotiation_intent"),
                        "reason": scenario.get("reason"),
                        "value": field_value
                    })

        return issues

    def _extract_numeric_value(self, value: str) -> Optional[float]:
        """
        Extract numeric value from a string with mixed content.
        Handles: '8.50% per annum', '₹16,750 per month', '42 months', etc.
        """
        if not value or not isinstance(value, str):
            return None
        
        # Remove currency symbols
        cleaned = value
        for symbol in ['$', '₹', '€', '£', '¥', 'Rs', 'rs', 'INR', 'USD', 'EUR', 'GBP']:
            cleaned = cleaned.replace(symbol, '')
        
        # Remove commas (handles both 1,000 and 1,00,000 formats)
        cleaned = cleaned.replace(',', '')
        
        # Extract the first numeric value (with optional decimal)
        match = re.search(r'[\d]+\.?\d*', cleaned)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None

    def _match_scenario(self, value: Any, scenario: Dict[str, Any],
                       normalized_unit: Optional[str]) -> bool:
        """Check if a value matches a scenario condition."""
        condition_type = scenario.get("condition_type", ConditionType.UNKNOWN)

        # Handle missing values
        if condition_type == ConditionType.MISSING:
            return value is None or (isinstance(value, str) and not value.strip())

        if value is None:
            return False

        # Handle text/regex conditions
        if condition_type == ConditionType.REGEX:
            patterns = scenario.get("regex_patterns", [])
            matched, _ = self.regex_evaluator.evaluate_text_field(value, patterns)
            return matched

        # Handle numeric conditions
        if condition_type in [ConditionType.NUMERIC, ConditionType.RANGE]:
            try:
                # Convert value to number using robust extraction
                if isinstance(value, str):
                    numeric_val = self._extract_numeric_value(value)
                else:
                    numeric_val = float(value)

                if numeric_val is None:
                    logger.warning(f"Could not extract numeric value from: {value}")
                    return False

                # Evaluate against condition
                _, condition_data = self.parser.parse(scenario.get("condition", ""))
                return self.parser.evaluate_numeric_condition(
                    condition_type, condition_data, numeric_val
                )
            except (ValueError, TypeError) as e:
                logger.warning(f"Error matching scenario for value '{value}': {e}")
                return False

        return False

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def export_cleaned_rules(self, rules: Dict[str, Any], format: str = "json") -> str:
        """
        Export cleaned rules in specified format.

        Args:
            rules: Processed rules dict
            format: Output format ("json", "yaml", etc.)

        Returns:
            Formatted rules string
        """
        if format == "json":
            return json.dumps(rules, indent=2, default=str)
        else:
            logger.warning(f"Format '{format}' not supported, using JSON")
            return json.dumps(rules, indent=2, default=str)
