import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# API Key Setup
os.environ["GROQ_API_KEY"] = "Groq API"

def generate_negotiation_message(vehicle_info, field_label, issue, intent):
    """
    Generates a polite, professional message for the user to send to the dealer.
    """
    try:
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
        
        prompt = PromptTemplate(
            template="""
            You are a professional negotiation assistant helping a customer with a car lease.
            
            Context:
            - Vehicle: {vehicle}
            - Contract Issue: {field} shows "{issue}"
            - Negotiation Goal: {intent}
            
            Task:
            Write a polite, professional, and firm message (2-3 sentences max) that the customer can copy and paste to the dealer.
            Do not include greetings like "Dear Dealer". Just the core message.
            """,
            input_variables=["vehicle", "field", "issue", "intent"]
        )
        
        chain = prompt | llm | StrOutputParser()
        
        result = chain.invoke({
            "vehicle": vehicle_info,
            "field": field_label,
            "issue": issue,
            "intent": intent
        })
        
        return result

    except Exception as e:
        print(f"Error generating message: {e}")
        return "Error generating negotiation message."
