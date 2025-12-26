import os
import requests
import json

def find_emails(query):
    url = "https://api.zo.computer/zo/ask"
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    
    prompt = f"""Use `gmail-find-email` for `attawar.v@gmail.com` with query: "{query}".
Return a raw JSON list of message objects. If none found, return []. No prose."""

    headers = {"authorization": token, "content-type": "application/json"}
    response = requests.post(url, headers=headers, json={"input": prompt})
    return response.json().get("output") if response.status_code == 200 else ""

if __name__ == "__main__":
    result = find_emails("newer_than:2d")
    print(result)
