# app/services/llm_extractor.py
import os
import json
import re
from groq import Groq


class LLMExtractor:
    """
    Robust extractor:
    ✔ Groq LLM extraction
    ✔ Regex fallback
    ✔ Clean numeric values
    ✔ Never crashes
    """

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if api_key:
            self.client = Groq(api_key=api_key)
            print("✅ Groq API connected")
        else:
            self.client = None
            print("⚠️ GROQ_API_KEY missing — using regex only")

    # =====================================================
    # MAIN METHOD
    # =====================================================

    def extract(self, text: str) -> dict:

        if self.client:
            data = self._extract_llm(text)

            if data and not data.get("error"):
                return data

        return self._regex_extract(text)

    # =====================================================
    # GROQ LLM EXTRACTION
    # =====================================================

    def _extract_llm(self, text: str) -> dict:

        try:
            prompt = f"""
Extract car lease contract data as JSON.

Fields:
vin, vehicle_make, vehicle_model, vehicle_year,
monthly_payment, down_payment, apr,
lease_term_months, mileage_allowance, dealer_price

Return ONLY valid JSON.
Use null if value missing.

Contract:
{text[:2000]}
"""

            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            content = completion.choices[0].message.content.strip()

            return self._clean_json(content)

        except Exception as e:
            print("❌ LLM error:", e)
            return {"error": str(e)}

    # =====================================================
    # CLEAN JSON FROM LLM
    # =====================================================

    def _clean_json(self, text: str) -> dict:

        try:
            start = text.find("{")
            end = text.rfind("}") + 1

            if start == -1:
                return {"error": "No JSON found"}

            data = json.loads(text[start:end])

            # Convert currency strings to numbers
            for k, v in data.items():

                if isinstance(v, str):
                    clean = v.replace(",", "").replace("₹", "").replace("$", "")

                    try:
                        data[k] = float(clean)
                    except:
                        data[k] = clean.strip()

            return data

        except Exception as e:
            return {"error": f"JSON parse error: {e}"}

    # =====================================================
    # REGEX FALLBACK (VERY IMPORTANT)
    # =====================================================

    def _regex_extract(self, text: str) -> dict:

        def find(pattern, cast=float):
            m = re.search(pattern, text, re.IGNORECASE)
            if not m:
                return None
            try:
                return cast(m.group(1).replace(",", ""))
            except:
                return None

        vin_match = re.search(r"\b([A-HJ-NPR-Z0-9]{17})\b", text)

        return {
            "vin": vin_match.group(1) if vin_match else None,
            "vehicle_make": None,
            "vehicle_model": None,
            "vehicle_year": find(r"\b(20\d{2})\b", int),

            "monthly_payment":
                find(r"Monthly Payment[:\s₹$]*([\d,]+)"),

            "down_payment":
                find(r"Down Payment[:\s₹$]*([\d,]+)"),

            "apr":
                find(r"APR[:\s]*([\d.]+)"),

            "lease_term_months":
                find(r"(\d+)\s*(?:month|mo)", int),

            "mileage_allowance":
                find(r"Mileage[:\s]*([\d,]+)", int),

            "dealer_price":
                find(r"(?:Price|MSRP|Total)[:\s₹$]*([\d,]+)")
        }