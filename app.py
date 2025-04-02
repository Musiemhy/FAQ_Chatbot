import os
import time
import json
import re
from hyperon import MeTTa
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv

load_dotenv()

# Retrieve your Gemini API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Error: GOOGLE_API_KEY not set in environment.")

# Initialize MeTTa instance
metta = MeTTa()

def call_llm_with_retry(prompt, retries=3, delay=10):
    """Call Gemini LLM with retry mechanism."""
    for attempt in range(retries):
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                temperature=0.5,
                google_api_key=api_key
            )
            response = llm.invoke(prompt)
            return response
        except ResourceExhausted:
            print(f"Quota exceeded. Retrying in {delay} seconds (Attempt {attempt+1}/{retries})...")
            time.sleep(delay)
    return None

def query_kg(query_string):
    """Query the knowledge graph using MeTTa."""
    try:
        with open("healthcare_kg.metta") as file:
            metta_data = file.read()
            metta.run(metta_data)
        result = metta.run(query_string)
        return result if result else None
    except Exception as e:
        print(f"Error during query execution: {e}")
        return None

def extract_structured_data(user_input):
    """Ask the LLM to extract structured data like disease names, medications, and query type."""
    prompt = (
        f"Extract the key information from the following medical query in JSON format. "
        f"Return an object with 'query_type' (symptoms, causes, treatment, side_effects, usage) "
        f"and either 'disease' or 'medication'.\n\n"
        f"User Query: {user_input}."
        f"And only send the required response no explanation and other things are required!"
    )
    response = call_llm_with_retry(prompt)

    if response is None:
        return None, "LLM returned None"

    # Extract content if it's an AIMessage
    if isinstance(response, AIMessage):
        response_text = response.content
    else:
        response_text = str(response)

    # Ensure response is valid
    if not response_text.strip():
        return None, "LLM returned an empty response"

    # remove ```json ... ```
    response_text = re.sub(r"^```json\n|\n```$", "", response_text).strip()

    try:
        structured_data = json.loads(response_text)
        return structured_data
    except json.JSONDecodeError:
        return None, "Invalid JSON format from LLM"

def process_query(user_input):
    """
    Processes the user query by using LLM for structured extraction, then querying the KG for facts, and then enriching the response with Gemini.
    """
    # Extract structured data from LLM
    structured_data = extract_structured_data(user_input)

    if not structured_data:
        structured_info = "I could not find this in my healthcare knowledge graph, but I will try to answer based on my general knowledge."

    query_type = structured_data.get("query_type")
    disease = structured_data.get("disease")
    medication = structured_data.get("medication")

    if disease:
        disease = disease.capitalize()
    if medication:
        medication = medication.capitalize()

    # Build the KG query based on extracted data
    kg_query = None
    if query_type == "symptoms" and disease:
        kg_query = f'!(match &self ({disease} $symptoms $causes) $symptoms)'
    elif query_type == "causes" and disease:
        kg_query = f'!(match &self ({disease} $symptoms $causes) $causes)'
    elif query_type == "treatment" and disease:
        kg_query = f'!(match &self ($y isMedicationFor {disease}) $y)'
    elif query_type == "side_effects" and medication:
        kg_query = f'!(match &self ({medication} $uses $sideEffects $dosage) $sideEffects)'
    elif query_type == "usage" and medication:
        kg_query = f'!(match &self ({medication} $uses $sideEffects $dosage) ($uses $dosage))'

    if kg_query:
        kg_result = query_kg(kg_query)
    
    if kg_result:
        structured_info = f"Structured data from the Healthcare Knowledge Graph: {kg_result}"
    else:
        structured_info = "I could not find this in my healthcare knowledge graph, but I will try to answer based on my general knowledge."
    
    messages = [
        SystemMessage(
            content=(
                "You are a domain-specific AI assistant specialized in healthcare. "
                "When a user asks a medical question, first check the healthcare knowledge graph. "
                "If the information is available, use it to generate a response. "
                "If the information is not found in the knowledge graph, provide a general AI-generated response "
                "while letting the user know that the answer is not sourced from the knowledge graph."
            )
        ),
        SystemMessage(content=structured_info),
        HumanMessage(content=user_input)
    ]

    response = call_llm_with_retry(messages)
    return response if response else "Sorry, I couldn't process your request."

def main():
    print("Healthcare Chatbot is ready. Type 'exit' to quit.")
    while True:
        user_input = input("\nAsk a healthcare question: ").strip()
        if user_input.lower() in ['exit', 'quit']:
            break
        
        answer = process_query(user_input)
        print("\nAnswer:\n", answer.content)

if __name__ == "__main__":
    main()