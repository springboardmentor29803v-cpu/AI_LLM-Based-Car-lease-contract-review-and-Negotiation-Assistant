# app/extractor.py - NEW SIMPLE VERSION
import os
import re
import json
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class AIExtractor:
    """
    Production-ready contract extractor
    Supports:
    ✔ Gemini (if key exists)
    ✔ Groq (if key exists)
    ✔ Regex fallback (always works)
    ✔ Returns clean numeric values
    """

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")

        print(f"🔑 Gemini: {'✅' if self.gemini_key else '❌'}")
        print(f"🔑 Groq: {'✅' if self.groq_key else '❌'}")

    # =========================================================
    # MAIN METHOD
    # =========================================================

    def extract(self, text: str) -> Dict[str, Any]:

        if self.gemini_key:
            data = self._extract_gemini(text)
            if data:
                return data

        if self.groq_key:
            data = self._extract_groq(text)
            if data:
                return data

        return self._regex_extract(text)

    # =========================================================
    # GEMINI EXTRACTION
    # =========================================================

    def _extract_gemini(self, text: str):

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel("models/gemini-2.0-flash")

            prompt = f"""
Extract car lease contract data as JSON.

Fields:
vin, vehicle_make, vehicle_model, vehicle_year,
apr, lease_term_months, monthly_payment,
down_payment, mileage_allowance, dealer_price

Return ONLY JSON. Use null for missing values.

Contract:
{text[:2000]}
"""

            response = model.generate_content(prompt)
            return self._clean_json(response.text)

        except Exception as e:
            print("Gemini error:", e)
            return None

    # =========================================================
    # GROQ EXTRACTION
    # =========================================================

    def _extract_groq(self, text: str):

        try:
            from groq import Groq

            client = Groq(api_key=self.groq_key)

            prompt = f"""
Extract car contract fields as JSON:
vin, vehicle_make, vehicle_model, vehicle_year,
apr, lease_term_months, monthly_payment,
down_payment, mileage_allowance, dealer_price

Return ONLY JSON.

Contract:
{text[:2000]}
"""

            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            content = completion.choices[0].message.content
            return self._clean_json(content)

        except Exception as e:
            print("Groq error:", e)
            return None

    # =========================================================
    # REGEX FALLBACK (VERY IMPORTANT)
    # =========================================================

    def _regex_extract(self, text: str) -> Dict[str, Any]:

        def find(pattern, cast=float):
            m = re.search(pattern, text, re.IGNORECASE)
            if not m:
                return None
            try:
                val = m.group(1).replace(",", "")
                return cast(val)
            except:
                return None

        vin_match = re.search(r"\b([A-HJ-NPR-Z0-9]{17})\b", text)

        return {
            "vin": vin_match.group(1) if vin_match else None,

            "vehicle_make": None,
            "vehicle_model": None,
            "vehicle_year": find(r"\b(20\d{2})\b", int),

            "apr": find(r"APR[:\s]*([\d.]+)"),

            "lease_term_months":
                find(r"(\d+)\s*(?:month|mo)", int),

            "monthly_payment":
                find(r"Monthly Payment[:\s₹$]*([\d,]+)"),

            "down_payment":
                find(r"Down Payment[:\s₹$]*([\d,]+)"),

            "mileage_allowance":
                find(r"Mileage[:\s]*([\d,]+)", int),

            "dealer_price":
                find(r"(?:Price|MSRP|Total)[:\s₹$]*([\d,]+)")
        }

    # =========================================================
    # CLEAN JSON FROM LLM
    # =========================================================

    def _clean_json(self, text: str):

        try:
            start = text.find("{")
            end = text.rfind("}") + 1

            if start == -1:
                return None

            data = json.loads(text[start:end])

            for k, v in data.items():
                if isinstance(v, str):
                    v = v.replace(",", "").replace("₹", "").replace("$", "")
                    try:
                        data[k] = float(v)
                    except:
                        data[k] = v.strip()

            return data

        except Exception as e:
            print("JSON parse error:", e)
            return None