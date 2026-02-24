import os
from langchain_core.output_parsers import PydanticOutputParser # <--- Use langchain_core
from langchain_core.prompts import PromptTemplate           # <--- Use langchain_core
from langchain_google_genai import ChatGoogleGenerativeAI
from models import LeaseContract
from dotenv import load_dotenv

load_dotenv()
# Now initialize the LLM - it will automatically look for GOOGLE_API_KEY or GEMINI_API_KEY

# Setup
parser = PydanticOutputParser(pydantic_object=LeaseContract)
# Now initialize the LLM - it will automatically look for GOOGLE_API_KEY or GEMINI_API_KEY
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    google_api_key=os.getenv("GEMINI_API_KEY"), # <--- Explicitly point to it
    temperature=0
)

prompt_template = PromptTemplate(
    template="Extract details from the text.\n{format_instructions}\nText: {text}\n",
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

def run_extraction(text):
    chain = prompt_template | llm | parser
    return chain.invoke({"text": text}).model_dump()
if __name__ == "__main__":
    print("✅ Logic loaded successfully!")
    print(f"Format Instructions generated: {parser.get_format_instructions()[:50]}...")