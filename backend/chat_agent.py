import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Ensure your professional environment variable is set
os.environ["GROQ_API_KEY"] = "groq API"

def chat_with_contract(contract_context: str, user_query: str):
    """
    High-level Negotiation Assistant logic using Llama 3.3.
    """
    try:
        # Lower temperature (0.3) ensures more consistent, professional results
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)
        
        prompt = PromptTemplate(
            template="""
            ROLE: You are 'ContractClarity AI', a high-level Senior Lease Negotiator. 
            TONE: Professional, authoritative, and strategic.
            
            CONTEXT:
            {context}
            
            USER QUERY:
            {question}
            
            STRICT RESPONSE GUIDELINES:
            1. Response MUST be exactly 2-3 sentences.
            2. Do NOT simply state facts; provide a strategic 'Next Step' or advice.
            3. Use professional vocabulary (e.g., "market standard," "leverage," "transparency").
            4. If a rate is high, suggest a specific counter-offer or question for the dealer.
            
            EXPERT ADVICE:
            """,
            input_variables=["context", "question"]
        )
        
        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"context": contract_context, "question": user_query})

    except Exception as e:
        return f"Strategic Analysis Error: {str(e)}"
