# app/services/llm_service.py
import os
from groq import Groq


class LLMService:
    """
    Strict Groq LLM wrapper
    Enforces deterministic, structured output
    """

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY not set")

        self.client = Groq(api_key=api_key)

    # ----------------------------------------------------
    # MAIN GENERATE FUNCTION
    # ----------------------------------------------------
    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 350
    ) -> str:

        response = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict financial negotiation AI. "
                        "Follow the user's template EXACTLY. "
                        "Do NOT add extra sections. "
                        "Do NOT explain. "
                        "Do NOT write reports. "
                        "Be concise."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.9
        )

        return response.choices[0].message.content.strip()


# Singleton instance
llm_service = LLMService()