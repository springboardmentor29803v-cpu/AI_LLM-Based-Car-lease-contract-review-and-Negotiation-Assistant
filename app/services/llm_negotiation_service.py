# app/services/llm_negotiation_service.py
# app/services/llm_negotiation_service.py

from typing import Dict, Any
from app.services.llm_service import llm_service


class LLMNegotiationService:
    """
    🌟 WORLD-CLASS AI Negotiation Advisor
    Fintech-grade decision support system
    """

    def __init__(self):
        self.llm = llm_service

    # ----------------------------------------------------
    # MAIN FUNCTION
    # ----------------------------------------------------
    def generate_negotiation_message(
        self,
        user_message: str,
        contract_data: Dict[str, Any],
        fairness_score: int,
        risk_level: str
    ) -> str:

        if not self.llm:
            return self._fallback()

        prompt = self._create_prompt(
            user_message,
            contract_data,
            fairness_score,
            risk_level
        )

        try:
            response = self.llm.generate(prompt)
            return response.strip()

        except Exception as e:
            print("❌ LLM Error:", e)
            return self._fallback()

    # ----------------------------------------------------
    # 🌟 WORLD-CLASS PROMPT
    # ----------------------------------------------------
    def _create_prompt(
        self,
        user_message: str,
        contract_data: Dict[str, Any],
        fairness_score: int,
        risk_level: str
    ) -> str:

        contract_text = "\n".join(
            f"{k.replace('_',' ').title()}: {v}"
            for k, v in contract_data.items()
            if v not in [None, "", 0]
        ) or "No contract data"

        return f"""
You are ContractCoach — an elite AI vehicle finance negotiation expert.

You analyze contracts like a senior financial advisor, not a chatbot.

AVAILABLE CONTEXT:
• Extracted contract data
• Pricing intelligence
• Risk analysis
• Market comparison
• Fairness scoring

CONTRACT DATA:
{contract_text}

FAIRNESS SCORE: {fairness_score}/100
RISK LEVEL: {risk_level}

USER QUESTION:
{user_message}

--------------------------------------

Generate a PREMIUM negotiation insight using this EXACT format:

🧾 Deal Insight  
One-sentence evaluation of the situation.

💰 Financial Impact  
Estimate potential savings or extra cost.

🧠 Recommended Strategy  
3 short bullet points with practical tactics.

🗣️ What To Say  
Provide one persuasive real-life sentence the user can speak.

⚠️ If You Don’t Negotiate  
Explain the downside in 1–2 lines.

📊 Confidence Level  
High / Medium / Low + reason.

🏁 Final Recommendation  
Clear action (Negotiate / Accept / Compare offers).

--------------------------------------

RULES:

• Keep under 220 words  
• Use clear consumer-friendly language  
• Avoid technical jargon  
• Be realistic and financially grounded  
• Do NOT mention being an AI  
• Do NOT invent external data sources  
"""

    # ----------------------------------------------------
    # FALLBACK
    # ----------------------------------------------------
    def _fallback(self) -> str:
        return (
            "🧾 Deal Insight\n"
            "Your APR appears slightly above market rates.\n\n"
            "💰 Financial Impact\n"
            "You may pay extra interest over the loan term.\n\n"
            "🧠 Recommended Strategy\n"
            "• Ask lender to match market APR\n"
            "• Compare offers from other banks\n"
            "• Consider higher down payment\n\n"
            "🗣️ What To Say\n"
            "\"If you can match a lower rate, I'm ready to proceed.\"\n\n"
            "⚠️ If You Don’t Negotiate\n"
            "You could pay unnecessary additional interest.\n\n"
            "📊 Confidence Level\n"
            "Medium — rate slightly above market.\n\n"
            "🏁 Final Recommendation\n"
            "Negotiate before signing."
        )