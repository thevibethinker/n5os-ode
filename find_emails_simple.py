import os
import requests
import json

def find_emails(query):
    url = "https://api.zo.computer/zo/ask"
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    
    prompt = f"""Use the tool `gmail-find-email` with the following query for the account `attawar.v@gmail.com`:
{query}

Return the result as a raw JSON list of the message objects found. No preamble, just the JSON list."""

    headers = {
        "authorization": token,
        "content-type": "application/json"
    }
    
    data = {
        "input": prompt
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("output")
    else:
        return f"Error: {response.status_code} - {response.text}"

if __name__ == "__main__":
    senders = ["hi@theagentic.ai", "newsletter@marvin.vc", "events@nextplay.so"]
    all_results = []
    for sender in senders:
        query = f"from:{sender} newer_than:2d"
        result = find_emails(query)
        try:
            # Clean potential preamble if any
            if result.startswith("```json"):
                result = result.split("```json")[1].split("```")[0].strip()
            elif result.startswith("```"):
                result = result.split("```")[1].split("```")[0].strip()
            
            items = json.loads(result)
            if isinstance(items, list):
                all_results.extend(items)
            elif isinstance(items, dict):
                all_results.append(items)
        except Exception as e:
            print(f"Failed to parse for {sender}: {e}")
            print(f"Raw output: {result}")
            
    print(json.dumps(all_results))
