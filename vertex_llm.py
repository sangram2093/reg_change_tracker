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

def get_summary_with_context(text, context=None):
    model = GenerativeModel(os.getenv("GEMINI_MODEL"))
    if context:
        prompt = f"""
                    You are an AI assistant for analyzing financial regulation documents.
                    
                    Explain the given regulation in detail. You as an assistant should resolve all of the cross references within the document.
                    
                    Input:
                    {text}
                    
                    Reference of the past year regulation entity relationship is given for your reference below. Use it only for semantic difference matching. Make sure you figure out the differences very clear in the above text and previous year's summarized text and provide the summary for this year based on above text.
                    
                    {context}
                """
    else:
        prompt = f"""
                    You are an AI assistant for analyzing financial regulation documents.
                    
                    Explain the given regulation in detail. You as an assistant should resolve all of the cross references within the document.
                    
                    Input:
                    {text}
                """
    response = model.generate_content(prompt, generation_config={"temperature": 0.01, "top_p": 0.1, "top_k": 40}))
    return response.text

def get_entity_relationship_with_context(text, context=None):
    model = GenerativeModel(os.getenv("GEMINI_MODEL"))
    if context:
        prompt = f"""
                    You are an AI assistant for analyzing financial regulation documents.
                    
                    For the given summary of the regulation, provide entity relationships in subject-verb-object, optionality, condition for relationship to be active, property of the object which is part of the condition, the frequency of condition validation and the actual thresholds where deutsche bank is licensed commercial bank. Consider the essential elements of an obligation such as active subject (creditor or obligee), passive subject (debtor or obligor) and prestation (object or subject matter of the obligation) and write the relationships in the above format with the perspective of deutsche bank as an obligor where the relationships will be useful for creating the standard operating procedures for the bank.
                    The verb should correspond to obligation and the conditions which make the obligation mandatory should be reported as conditions. For e.g. Deutsche bank grants a loan to any customer has no meaning from the obligation perspective but a granting of a loan is a condition which obligates Deutsche bank to report the loan and associated attributes. 
                    You as an assistant should resolve all of the cross references within the document. Assign each entity a globally unique ID.

                    Respond in valid JSON ONLY. Make sure you follow below JSON structure.
                    
                    {
                        "entities": [
                            {"id": "E1", "name": "Deutsche Bank (LCB)", "type": "organization"}
                        ],
                        "relationships": [
                            {"subject_id": "E1", 
                             "subject_name": "Deutsche Bank (LCB)", 
                             "verb": "Reports", 
                             "object_id": "E2", 
                             "object_name": "Loan (to Prime Customer)",
                             "Optionality": "Conditional (Only if eligible loans exist)", 
                             "Condition for Relationship to be Active": "Loan disbursed to a Prime Customer during the reporting week, meets eligibility criteria (short-term, overdraft, etc.), and exceeds LKR 10 million (or LKR 1 million if no loans exceed LKR 10 million)",
                             "Property of Object (part of condition)": "Disbursed amount, Borrower classification (Prime Customer), Loan type (short-term, overdraft), Currency (LKR), Customer type (Private Sector)", "Thresholds": "LKR 10 million (general reporting) or LKR 1 million (for individual bank publication only if no loans exceed LKR 10 million)", 
                             "frequency": "to be validated quarterly"}
                        ]
                    }
                    
                    Make a strict note of responding in valid JSON only. Don’t explain.
                    Input:
                    {text}

                    Reference of the past year regulation entity relationship is given for your reference below. Use it only for semantic difference matching.

                    {context}
                """
    else:
        prompt = f"""
                    You are an AI assistant for analyzing financial regulation documents.
                    
                    For the given summary of the regulation, provide entity relationships in subject-verb-object, optionality, condition for relationship to be active, property of the object which is part of the condition, the frequency of condition validation and the actual thresholds where deutsche bank is licensed commercial bank. Consider the essential elements of an obligation such as active subject (creditor or obligee), passive subject (debtor or obligor) and prestation (object or subject matter of the obligation) and write the relationships in the above format with the perspective of deutsche bank as an obligor where the relationships will be useful for creating the standard operating procedures for the bank.
                    The verb should correspond to obligation and the conditions which make the obligation mandatory should be reported as conditions. For e.g. Deutsche bank grants a loan to any customer has no meaning from the obligation perspective but a granting of a loan is a condition which obligates Deutsche bank to report the loan and associated attributes. 
                    You as an assistant should resolve all of the cross references within the document. Assign each entity a globally unique ID.

                    Respond in valid JSON ONLY. Make sure you follow below JSON structure.
                    
                    {
                        "entities": [
                            {"id": "E1", "name": "Deutsche Bank (LCB)", "type": "organization"}
                        ],
                        "relationships": [
                            {"subject_id": "E1", 
                             "subject_name": "Deutsche Bank (LCB)", 
                             "verb": "Reports", 
                             "object_id": "E2", 
                             "object_name": "Loan (to Prime Customer)",
                             "Optionality": "Conditional (Only if eligible loans exist)", 
                             "Condition for Relationship to be Active": "Loan disbursed to a Prime Customer during the reporting week, meets eligibility criteria (short-term, overdraft, etc.), and exceeds LKR 10 million (or LKR 1 million if no loans exceed LKR 10 million)",
                             "Property of Object (part of condition)": "Disbursed amount, Borrower classification (Prime Customer), Loan type (short-term, overdraft), Currency (LKR), Customer type (Private Sector)", "Thresholds": "LKR 10 million (general reporting) or LKR 1 million (for individual bank publication only if no loans exceed LKR 10 million)", 
                             "frequency": "to be validated quarterly"}
                        ]
                    }
                    
                    Make a strict note of responding in valid JSON only. Don’t explain.
                    Input:
                    {text}
                """
    response = model.generate_content(prompt, generation_config={"temperature": 0.01, "top_p": 0.1, "top_k": 40}))
    match = re.search(r'(\{.*\})', response.text, re.DOTALL)
    if match:
        json_text = match.group(1)
        json.loads(json_text)
        return json_text
    else:
        raise ValueError("Invalid JSON returned by Gemini")

def get_kop_doc(new_summary, new_json_str):
    model = GenerativeModel(os.getenv("GEMINI_MODEL"))
    prompt = f"""
                You are an AI assistant for analyzing financial regulation documents and generating a clear Key Operating Procedures (KOP) out of it.
                
                Given the original document, pickup the modality of reporting.
                
                {new_summary}
                
                Given this particular graph, pickup the necessary actions to be performed.
                
                {new_json_str}
                
                Generate a KOP document with step wise instruction for operational personnel.
            """
    response = model.generate_content(prompt, generation_config={"temperature": 0.01, "top_p": 0.1, "top_k": 40}))
    return response.text
