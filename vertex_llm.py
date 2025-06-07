import os
import re
import json
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
import vertexai
from vertexai.generative_models import GenerativeModel

load_dotenv()

def init_vertexai():
    token_path = os.path.join(os.getenv("WIF_HOME"), "wif_token.txt")
    with open(token_path, "r") as f:
        access_token = f.read().strip()
    credentials = Credentials(token=access_token, scopes=["https://www.googleapis.com/auth/cloud-platform"])
    vertexai.init(project=os.getenv("PROJECT_NAME"), location=os.getenv("LOCATION"), credentials=credentials)

def get_summary_entities(text, version="latest"):
    model = GenerativeModel(os.getenv("GEMINI_MODEL"))
    prompt = f"""
You are an AI assistant for analyzing financial regulation documents.

From the following regulation text:
1. Extract all relevant entities (organizations, individuals, obligations, processes).
2. Assign each entity a globally unique ID.
3. Identify relationships between entities using subject-verb-object form.
4. Include a confidence_score (between 0 and 1) for each relationship.

Respond in valid JSON ONLY:
{{ "entities": [...], "relationships": [...] }}

Input:
{text}
"""
    response = model.generate_content(prompt)
    match = re.search(r'(\{.*\})', response.text, re.DOTALL)
    if match:
        json_text = match.group(1)
        json.loads(json_text)
        return json_text
    else:
        raise ValueError("Invalid JSON returned by Gemini")
