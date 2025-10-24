from google import genai
from pydantic import BaseModel
import json
import PyPDF2
import os
from groq import Groq
from dotenv import load_dotenv
from google.genai import types
load_dotenv()

# ********   Phase 1    ******** #
def  Clause_extraction(file):
    print("inside clause extraction")
    class ClauseExtraction(BaseModel):
        clause_id: str
        heading: str
        text: str

    text=" "
    with open(file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    you are an expert in legal contract analysis.
    Your task is to extract all **clauses** from the following contract text.

    ### Guidelines:
    - A clause may begin with:
      - A number/letter (e.g. "1.", "A."),
      - The word "Clause" followed by a number (e.g. "Clause 1", "Clause 5"),
      - An ALL CAPS heading (e.g. "DEFINATION", "TRANSFER OF DATA".)

    - Each extracted clause must include:
      - **clause_id** (the exact numbering/label from the contract e.g. "1.", "A.", "Clause 1", "EXHIBIT A" etc)
      - **heading/title** (use explicit heading if present; else first few words of the clause)
      - **full text** (the complete text of the clause, including any sub-clauses)

    - Maintain clause boundaries precisely. Do not merge multiple clauses.
    - Include clauses from exhibits, appendices, annexes.
    - Response in **valid JSON** only.

    Input: {text}

    Response in this JSON Structure:
    [
      {{
        "clause_id": "<clause_id>",
        "heading/title": "<heading_or_title>",
        "full text": "<full_text_of_clause>"
      }},
      ...
    ]
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0), #Disable thinking
            response_mime_type="application/json",
            response_schema=list[ClauseExtraction],
        ),
    )

    response = response.text
    print(response)
    return response

if __name__ == "__main__":
    # for normal flow
    response = Clause_extraction("(SCCs) Standard Contractual Clauses.pdf")

    with open("scc_sum.json", "w", encoding="utf-8") as f:
        json.dump(response, f, indent=2, ensure_ascii=False)