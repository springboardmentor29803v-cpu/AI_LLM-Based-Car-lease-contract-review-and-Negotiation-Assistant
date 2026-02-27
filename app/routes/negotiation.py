from fastapi import APIRouter, HTTPException
from app.database import SessionLocal, Contract
from app.services.rules_engine import analyze_contract
from app.services.llm_negotiation_service import LLMNegotiationService

router = APIRouter()
negotiator = LLMNegotiationService()


@router.get("/{contract_id}/negotiate")
def negotiate_contract(contract_id: int):

    db = SessionLocal()

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    # -----------------------------------------
    # Rule-based analysis
    # -----------------------------------------
    rule_analysis = analyze_contract(contract)

    # ✅ SAFE extraction (no KeyError)
    fairness_score = rule_analysis.get("fairness_score", 70)
    risk_level = rule_analysis.get("risk_level", "Medium")

    # -----------------------------------------
    # Convert contract object → dict
    # -----------------------------------------
    contract_data = contract.__dict__.copy()
    contract_data.pop("_sa_instance_state", None)

    # -----------------------------------------
    # 🌟 AI Negotiation Advice
    # -----------------------------------------
    ai_advice = negotiator.generate_negotiation_message(
        user_message="Provide negotiation advice",
        contract_data=contract_data,
        fairness_score=fairness_score,
        risk_level=risk_level
    )

    return {
        "success": True,
        "vehicle": f"{contract.vehicle_make} {contract.vehicle_model}",
        "risk_level": risk_level,
        "fairness_score": fairness_score,
        "ai_negotiation_advice": ai_advice
    }