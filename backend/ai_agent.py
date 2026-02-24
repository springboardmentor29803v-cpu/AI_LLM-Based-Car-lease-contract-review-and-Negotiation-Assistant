import os
import json
import re
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from schemas import LeaseContractSLA

# API Key Setup
os.environ["GROQ_API_KEY"] = "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"

def repair_ocr_typos(text: str):
    """
    Fixes common OCR errors where symbols like '₹' or '1' are read as 'I'.
    Example: 'I12,000' -> '12,000' and 'I8' -> '8'.
    """
    if not text:
        return text

    # Pattern: Look for Capital 'I' followed immediately by a digit (0-9)
    # This fixes "I8" -> "8" and "I12,000" -> "12,000"
    fixed_text = re.sub(r'\bI(\d)', r'\1', text) 
    
    # Also fix cases where it might be inside a string like "Amount: I200"
    fixed_text = re.sub(r' I(\d)', r' \1', fixed_text)

    return fixed_text

def clean_and_extract_json(text: str):
    """
    Robust function to find the JSON object inside a messy string.
    """
    try:
        # 1. Run the Repair Function FIRST on the raw text result
        text = repair_ocr_typos(text)

        match = re.search(r"(\{.*\})", text, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            return json.loads(json_str)
        else:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
            return None
            
    except Exception as e:
        print(f"JSON Cleaning Error: {e}")
        return None

def extract_lease_data(contract_text: str):
    """
    Uses Llama 3.3 to extract ALL 15 SLA fields + Identity info.
    """
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0
        )
        
        # (Your existing PromptTemplate code remains exactly the same here)
        prompt = PromptTemplate(
            template="""
            You are an AI legal assistant. Analyze the vehicle agreement below.
            
            EXTRACT THESE SPECIFIC SLA FIELDS (JSON format):
            
            1. interest_rate_apr (float)
            2. lease_term_months (int)
            3. monthly_payment (float)
            4. down_payment (float)
            5. residual_value (float)
            6. mileage_allowance (string)
            7. mileage_overage_charge (string)
            8. buyout_price (float)
            9. early_termination_fee (string)
            10. maintenance_responsibilities (string)
            11. warranty_coverage (string)
            12. insurance_requirements (string)
            13. late_fee_policy (string)
            14. vehicle_year (int)
            15. recalls_text (string)

            IDENTITY FIELDS:
            - vin_number
            - vehicle_make
            - vehicle_model

            OUTPUT ONLY VALID JSON. Use null if not found.
            
            CONTRACT TEXT:
            {text}
            """,
            input_variables=["text"],
        )

        print("--- 🤖 Invoking Llama 3.3 (Full SLA Extraction)... ---")
        chain = prompt | llm | StrOutputParser()
        
        raw_result = chain.invoke({"text": contract_text})
        
        # The cleaning now happens inside this function automatically
        cleaned_data = clean_and_extract_json(raw_result)
        
        if cleaned_data:
            print("✅ SLA JSON Extracted & Repaired Successfully")
            return cleaned_data
        else:
            print("❌ AI returned text, but valid JSON was not found.")
            return {}

    except Exception as e:
        print(f"Error in Groq extraction: {e}")
        return {}
