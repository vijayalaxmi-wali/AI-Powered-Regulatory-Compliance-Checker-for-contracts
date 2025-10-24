from google import genai
from google.genai import types
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from enum import Enum
import PyPDF2
import json
import os

from groq import Groq

# question= "what kind of document is this ?"
# answer= "This is a Data Processing Agreement"

load_dotenv()

# ********   Phase 2    ******** #
def document_type(file):
    
    class DocumentType(str, Enum):
        DPA= "Data Processing Agreement"
        JCA= "Joint Controller Agreement"
        C2C= "Controller-to-Controller Agreement"
        subprocessor= "Processor-to-Subprocessor Agreement"
        SCC= "Standard Contractual Clauses"
        NoOne="NoOne"
    
    class FindDocumentType(BaseModel):
        document_type: DocumentType
        
        
    text=""
    with open(file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
            
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    # print(os.getenv("GEMINI_API_KEY"))
    prompt=f"""
        Tell me what type of document is this
        
        document should be type of between 
        
        1. Data Processing Agreement
        2. Joint Controller Agreement
        3. Controller-to-Controller Agreement
        4. Processor-to-Subprocessor Agreement
        5. Standard Contractual Clauses
        
        Input: {text}
        
        Response in this JSON Structure:
        [{{
            "document_type": "<type_of_document>"
        }},
        ]

    """
    response = client.models.generate_content(
        model ="gemini-2.5-flash", contents=prompt,
        # config={
        #     "response_mime_type":"application/json",
        #     "response_schema": list[FindDocumentType],
        # }
        config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking
                response_mime_type="application/json",
                response_schema=list[FindDocumentType],
            ),
        )
    json_object = json.loads(response.text)
    # print(json_object[0]['document_type'])
    return json_object[0]['document_type']




def compare_agreements(unseen_data, template_data):
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    
    prompt=f"""
    You are an AI legal assistant specialized in contract review and compliance.

    Compare the two documents below:

    Template document (regulatory standard reference): 
    {template_data}

    New contract document to review:
    {unseen_data}

    Tasks:
    1. Identify any missing or altered clauses in the new contract compared to the template.
    2. Flag potential compliance risks based on GDPR regulations.
    3. Assign a risk score between 0 and 100 for the new contract (0 = no risk, 100 = maximum risk).
    4. Provide reasoning for the assigned risk score.
    5. Suggest specific amendments or recommendations to bring the contract in line with current regulatory standards and best practices.
    6. Provide the response in a **concise, structured format**, like this:

    - Missing Clauses: [...]
    - Potential Compliance Risks: [...]
    - Risk Score (0-100): ...
    - Reasoning: [...]
    - Recommendations: [...]

    Keep each section brief and focused on key points. Avoid long paragraphs or unnecessary details.

    """
    
    response = client.models.generate_content(
        model ="gemini-2.5-flash", contents=prompt,
        config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking
                temperature=0.3
            ),

        )
    return response.text