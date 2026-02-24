import json
import re
from negotiation_agent import generate_negotiation_message
from market_service import analyze_financial_fairness

def load_rules():
    try:
        with open("sla_rules.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading rules: {e}")
        return []

def parse_numeric(value):
    """Cleans strings like '₹ 12,000' -> 12000.0"""
    if not value: return None
    if isinstance(value, (int, float)): return float(value)
    clean = re.sub(r"[^\d.]", "", str(value))
    try: return float(clean)
    except: return None

def check_condition(user_val, condition):
    val = parse_numeric(user_val)

    # 1. Missing Check
    if condition == "missing":
        return user_val is None

    # 2. Text Checks
    if isinstance(user_val, str):
        if condition == "contains_all_payments" and ("remaining" in user_val.lower() or "balance" in user_val.lower()):
            return True
        if condition == "lessee_pays_all" and "lessee" in user_val.lower() and "all" in user_val.lower():
            return True
        if condition == "strict_grace_period" and "5 days" in user_val.lower():
            return True
        if condition == "found" and user_val: 
            return True

    # 3. Numeric Checks
    if val is not None:
        if condition.startswith(">"):
            limit = float(condition.replace(">", "").strip())
            return val > limit
        if condition.startswith("<"):
            limit = float(condition.replace("<", "").strip())
            return val < limit

    return False

def calculate_fairness_score(issues_list):
    score = 100
    for item in issues_list:
        severity = item.get("severity", "none").lower()
        if severity == "high":
            score -= 20
        elif severity == "medium":
            score -= 10
            
    if score < 0: score = 0
    
    if score >= 90:
        grade = "A (Excellent)"
        color = "green"
    elif score >= 80:
        grade = "B (Good)"
        color = "blue"
    elif score >= 70:
        grade = "C (Fair)"
        color = "#FFcc00" # Yellow/Orange
    elif score >= 60:
        grade = "D (Poor)"
        color = "orange"
    else:
        grade = "F (Bad Deal)"
        color = "red"

    return {
        "score": score,
        "grade": grade,
        "color_code": color
    }

def analyze_contract(extracted_data):
    rules = load_rules()
    report = []
    
    vehicle_info = f"{extracted_data.get('vehicle_year', '')} {extracted_data.get('vehicle_make', '')} {extracted_data.get('vehicle_model', '')}"

    print("--- ⚖️ Running Rules Engine... ---")

    # 1. Check Standard Rules
    for rule in rules:
        field_key = rule["field"]
        user_value = extracted_data.get(field_key)
        
        matched_scenario = None
        for scenario in rule["scenarios"]:
            if check_condition(user_value, scenario["condition"]):
                matched_scenario = scenario
                break
        
        if matched_scenario:
            intent = matched_scenario["negotiation_intent"]
            print(f"   ⚠️ Issue found in {rule['label']}: Generating advice...")
            
            ai_message = generate_negotiation_message(
                vehicle_info=vehicle_info,
                field_label=rule["label"],
                issue=matched_scenario["issue"],
                intent=intent
            )

            report.append({
                "field": rule["label"],
                "value_found": user_value,
                "severity": matched_scenario["severity"],
                "issue": matched_scenario["issue"],
                "negotiation_intent": intent,
                "generated_chat_message": ai_message
            })

    # 2. Check Market Value
    payment = parse_numeric(extracted_data.get("monthly_payment"))
    make = extracted_data.get("vehicle_make")
    model = extracted_data.get("vehicle_model")
    year = extracted_data.get("vehicle_year")

    if payment and make:
        market_analysis = analyze_financial_fairness(payment, make, model, year)
        if market_analysis["severity"] == "high":
            price_msg = generate_negotiation_message(
                 vehicle_info=vehicle_info,
                 field_label="Monthly Payment",
                 issue=f"Overpriced ({market_analysis['fair_market_range']})",
                 intent=market_analysis["advice"]
            )
            report.append({
                "field": "Market Price Check",
                "value_found": f"₹{payment}",
                "severity": "high",
                "issue": "Payment Above Market Value",
                "negotiation_intent": market_analysis["advice"],
                "generated_chat_message": price_msg
            })

    # 3. Calculate Score
    score_card = calculate_fairness_score(report)

    # 4. Return Structured Dict (THIS FIXES YOUR ERROR)
    return {
        "risk_analysis": report,
        "fairness_score": score_card
    }
