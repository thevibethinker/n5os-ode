import os
import requests
import json
import re

def find_emails(query):
    url = "https://api.zo.computer/zo/ask"
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    
    prompt = f"""Search Gmail (attawar.v@gmail.com) for: "{query}".
Return ONLY a raw JSON list of message objects. No conversational text."""

    headers = {"authorization": token, "content-type": "application/json"}
    response = requests.post(url, headers=headers, json={"input": prompt})
    if response.status_code == 200:
        text = response.json().get("output", "[]")
        # Extract JSON from markdown if necessary
        match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
        if match:
            return match.group(0)
        return text
    return "[]"

if __name__ == "__main__":
    query = "from:(hi@theagentic.ai OR newsletter@marvin.vc OR events@nextplay.so) newer_than:2d"
    result = find_emails(query)
    print(result)
