
# app/services/rules_engine.py

def analyze_contract(contract):
    """
    Deterministic fairness + risk analysis
    """

    monthly = contract.monthly_payment or 0
    apr = contract.apr or 0
    term = contract.lease_term_months or 0
    mileage = int(contract.mileage_allowance or 0)

    issues = []
    suggestions = []
    risk = "Low"

    # APR analysis
    if apr > 10:
        issues.append("High interest rate")
        suggestions.append("Request lower APR or refinance options")
        risk = "High"
    elif apr > 7:
        issues.append("Moderately high interest rate")
        suggestions.append("Negotiate APR reduction")

    # Monthly payment
    if monthly > 800:
        issues.append("High monthly payment")
        suggestions.append("Ask for longer tenure or price reduction")
        risk = "Medium"

    # Mileage allowance
    if mileage and mileage < 10000:
        issues.append("Low mileage allowance")
        suggestions.append("Request higher mileage limit")

    # Term check
    if term > 72:
        issues.append("Very long loan term")
        suggestions.append("Consider shorter tenure to reduce interest")

    return {
        "issues": issues,
        "suggestions": suggestions,
        "risk_level": risk
    }