"""
Test and demonstration of the Rule Processing Layer.

Shows how to:
1. Load cleaned rules ONCE at startup (not on every request)
2. Cache the cleaned rules
3. Detect issues in contract data using cached rules
4. Extract negotiation intents
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.rule_processor import RuleProcessor, Severity, ConditionType
from app.services.rules_cache import initialize_rules_cache, get_cached_rules


def test_rule_processor():
    """Test the Rule Processing Layer with example data."""
    print("\n" + "=" * 80)
    print("RULE PROCESSING LAYER - DEMONSTRATION")
    print("=" * 80 + "\n")

    # ========================================================================
    # STARTUP: Load cleaned rules ONCE (happens at app startup, not per request)
    # ========================================================================
    print("1. STARTUP: LOAD CLEANED RULES (ONE-TIME OPERATION)")
    print("-" * 80)
    print("Loading rules from cleaned_rules.json...")
    
    cleaned_rules = initialize_rules_cache()
    
    print(f"✓ Loaded {len(cleaned_rules.get('fields', []))} field rules")
    print(f"✓ Total scenarios: {sum(len(f.get('scenarios', [])) for f in cleaned_rules.get('fields', []))}")
    print("✓ Rules cached globally (ready for reuse)")
    print("✓ You can now call get_cached_rules() multiple times without reloading\n")

    # ========================================================================
    # REUSE: Get cached rules (no reloading)
    # ========================================================================
    print("2. REUSE CACHED RULES (INSTANT, NO RELOADING)")
    print("-" * 80)
    print("Getting rules from cache...")
    
    cached_rules = get_cached_rules()
    
    print(f"✓ Retrieved {len(cached_rules.get('fields', []))} field rules from cache")
    print("✓ Instant retrieval - no processing overhead\n")

    # 2. Show example of cleaned rule
    print("\n3. EXAMPLE - CLEANED APR RULE:")
    print("-" * 80)
    apr_rule = cleaned_rules['fields'][0]
    print(f"Field: {apr_rule['field']}")
    print(f"Type: {apr_rule['field_type']}")
    print(f"Original Unit: {apr_rule['unit']}")
    print(f"Normalized Unit: {apr_rule['normalized_unit']}")
    print(f"Scenarios:")
    for i, scenario in enumerate(apr_rule['scenarios'], 1):
        print(f"  [{i}] Condition: {scenario['condition']} → Type: {scenario['condition_type']}")
        print(f"      Severity: {scenario['severity']}")
        print(f"      Issue: {scenario['issue']}")
        print(f"      Intent: {scenario['negotiation_intent']}")

    # 3. Test issue detection with sample contract data
    print("\n4. ISSUE DETECTION - REUSING CACHED RULES:")
    print("-" * 80)

    sample_contract = {
        "apr": "9.5%",
        "lease_term_months": "72",
        "monthly_payment": "1200",
        "down_payment": "$2500",
        "residual_value": "42%",
        "mileage_allowance": "8000",
        "late_fees": "5% per month AND $50 fixed fee",
        "early_termination_clause": "Full remaining balance due",
        "purchase_option": "Requires inspection"
    }

    print("Contract Data:")
    for key, value in sample_contract.items():
        print(f"  {key}: {value}")

    # Initialize processor for issue detection
    processor = RuleProcessor()
    
    # Convert to CleanedRule format for detection
    issues = processor.detect_issues(sample_contract, cleaned_rules)

    print(f"\nDetected Issues ({len(issues)}):")
    for i, issue in enumerate(issues, 1):
        print(f"  [{i}] Field: {issue['field']}")
        print(f"      Severity: {issue['severity']}")
        print(f"      Issue: {issue['issue']}")
        print(f"      Intent: {issue['negotiation_intent']}")
        print()

    # 4. Test condition parser
    print("5. CONDITION PARSER TEST:")
    print("-" * 80)
    test_conditions = [
        "missing",
        "<=6",
        "6-8",
        ">8",
        "<10000",
        "10000-15000",
        "regex:full_balance_due",
        ">20_percent"
    ]

    for condition in test_conditions:
        cond_type, cond_data = processor.parser.parse(condition)
        print(f"  '{condition}' → Type: {cond_type.value}, Data: {cond_data}")

    # 5. Test currency/percentage conversion
    print("\n6. CURRENCY & PERCENTAGE CONVERSION:")
    print("-" * 80)
    test_values = [
        ("8%", "percentage"),
        ("8", "percentage"),
        ("$1,500", "currency"),
        ("₹1,50,000", "currency"),
        ("€500", "currency"),
    ]

    for value, test_type in test_values:
        if test_type == "percentage":
            result = processor.converter.percentage_to_decimal(value)
            print(f"  {value} → {result} (decimal)")
        elif test_type == "currency":
            result = processor.converter.currency_to_number(value)
            print(f"  {value} → {result} (numeric)")

    # 6. Test numeric evaluation
    print("\n7. NUMERIC CONDITION EVALUATION:")
    print("-" * 80)
    test_cases = [
        ("<=6", 5, True),
        ("<=6", 6, True),
        ("<=6", 7, False),
        (">8", 8, False),
        (">8", 9, True),
        ("10000-15000", 12000, True),
        ("10000-15000", 9999, False),
    ]

    for condition, value, expected in test_cases:
        cond_type, cond_data = processor.parser.parse(condition)
        result = processor.parser.evaluate_numeric_condition(cond_type, cond_data, value)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {condition} with {value} = {result} (expected {expected})")

    # 7. Export cleaned rules
    print("\n8. EXPORTING CLEANED RULES (OPTIONAL BACKUP):")
    print("-" * 80)
    exported = processor.export_cleaned_rules(cleaned_rules)
    print("✓ Rules exported as JSON")
    print(f"  Size: {len(exported)} characters")
    print("  (Useful for backing up or sharing cleaned rules)\n")

    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80 + "\n")


def test_regex_engine():
    """Test the regex engine."""
    print("\n" + "=" * 80)
    print("REGEX ENGINE TEST")
    print("=" * 80 + "\n")

    processor = RuleProcessor()

    # Test regex evaluation
    print("Testing Regex Pattern Matching:")
    print("-" * 80)

    test_cases = [
        ("late_fees", "Payment is 2 weeks late, 5% late fee charged", True),
        ("early_termination", "Customer wants early termination, full balance due", True),
        ("purchase_option", "Vehicle inspection required before purchase", True),
        ("hidden_penalties", "Excess mileage charges at $0.25 per mile", True),
    ]

    for clause, text, should_match in test_cases:
        matched, matches = processor.regex_evaluator.evaluate_clause(text, clause)
        status = "✓" if matched == should_match else "✗"
        print(f"  {status} Clause '{clause}' in text: {matched}")
        if matched:
            print(f"      Matches: {matches}")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    test_rule_processor()
    test_regex_engine()
