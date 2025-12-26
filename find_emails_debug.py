import os
import requests
import json
import re

def find_emails(query):
    url = "https://api.zo.computer/zo/ask"
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    
    prompt = f"""Search Gmail (attawar.v@gmail.com) for: {query}.
Return ONLY the raw JSON result from `gmail-find-email`. If you encounter an "Unknown error", try searching for each sender individually and combine the results.
The senders are: hi@theagentic.ai, newsletter@marvin.vc, events@nextplay.so.
Format the output as a single JSON list. No prose."""

    headers = {"authorization": token, "content-type": "application/json"}
    response = requests.post(url, headers=headers, json={"input": prompt})
    return response.json().get("output", "[]")

if __name__ == "__main__":
    query = "from:(hi@theagentic.ai OR newsletter@marvin.vc OR events@nextplay.so) newer_than:2d"
    result = find_emails(query)
    print(result)
