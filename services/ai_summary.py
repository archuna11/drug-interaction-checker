import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_ai_summary(drugs, interactions, mode="doctor"):

    drug_names = [d.get("drug_name", "") for d in drugs]

    interaction_text = ""
    for i in interactions:
        interaction_text += f"""
        {i.get('drug1')} + {i.get('drug2')}
        Severity: {i.get('severity')}
        Description: {i.get('description')}
        Recommendation: {i.get('recommendation')}
        """

    if mode == "doctor":
        prompt = f"""
You are a clinical decision support system.

Patient medications: {drug_names}

Interactions:
{interaction_text}

Give a concise clinical summary with risks and recommendations.
"""
    else:
        prompt = f"""
Explain in simple terms for a patient:

Medications: {drug_names}

Interactions:
{interaction_text}

Keep it short and easy to understand.
"""

    response = requests.post(OLLAMA_URL, json={
        "model": "llama3.2:3b ",
        "prompt": prompt,
        "stream": False
    })

    data = response.json()
    return data.get("response") or data.get("message", {}).get("content", "Summary not available")