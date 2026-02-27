# app/services/fairness_engine.py

def calculate_fairness(data: dict):

    score = 100
    reasons = []

    apr = data.get("apr", 0)
    down_payment = data.get("down_payment", 0)
    monthly_payment = data.get("monthly_payment", 0)
    lease_term = data.get("lease_term_months", 0)

    # ==========================
    # APR Evaluation
    # ==========================
    if apr > 12:
        score -= 25
        reasons.append("APR is significantly higher than market average.")
    elif apr > 9:
        score -= 15
        reasons.append("APR is slightly above ideal range.")

    # ==========================
    # Down Payment Evaluation
    # ==========================
    if down_payment > 8000:
        score -= 15
        reasons.append("Down payment is high.")
    elif down_payment > 5000:
        score -= 8
        reasons.append("Down payment is moderately high.")

    # ==========================
    # Monthly Payment Evaluation
    # ==========================
    if monthly_payment > 900:
        score -= 20
        reasons.append("Monthly payment is very high.")
    elif monthly_payment > 700:
        score -= 10
        reasons.append("Monthly payment is above average.")

    # ==========================
    # Lease Term Check
    # ==========================
    if lease_term > 60:
        score -= 5
        reasons.append("Lease term is long.")

    # ==========================
    # Risk Level
    # ==========================
    if score >= 80:
        risk_level = "Low"
    elif score >= 60:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # ==========================
    # Negotiation Strength
    # ==========================
    if risk_level == "High":
        negotiation_strength = "Strong"
    elif risk_level == "Medium":
        negotiation_strength = "Moderate"
    else:
        negotiation_strength = "Limited"

    # ==========================
    # Recommendation
    # ==========================
    if negotiation_strength == "Strong":
        recommendation = "You are in a strong position to negotiate. Push for APR reduction and lower upfront costs."
    elif negotiation_strength == "Moderate":
        recommendation = "There is room for negotiation. Focus on monthly payment adjustments."
    else:
        recommendation = "The contract appears relatively fair. Minor negotiation is recommended."

    # ==========================
    # Confidence Score
    # ==========================
    confidence_score = round(score / 100, 2)

    return {
        "fairness_score": score,
        "risk_level": risk_level,
        "negotiation_strength": negotiation_strength,
        "risk_reason": " | ".join(reasons) if reasons else "No major risk factors detected.",
        "recommendation": recommendation,
        "confidence_score": confidence_score
    }