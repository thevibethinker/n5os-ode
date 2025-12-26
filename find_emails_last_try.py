import os
import requests
import json

def ask_zo(prompt):
    url = "https://api.zo.computer/zo/ask"
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    headers = {"authorization": token, "content-type": "application/json"}
    response = requests.post(url, headers=headers, json={"input": prompt})
    return response.json().get("output", "[]")

if __name__ == "__main__":
    senders = ["hi@theagentic.ai", "newsletter@marvin.vc", "events@nextplay.so"]
    all_emails = []
    for s in senders:
        res = ask_zo(f"Search attawar.v@gmail.com for `from:{s} newer_than:2d` and return the JSON list of messages.")
        # Very crude extraction
        if "[" in res and "]" in res:
            try:
                emails = json.loads(res[res.find("["):res.rfind("]")+1])
                all_emails.extend(emails)
            except:
                pass
    print(json.dumps(all_emails))
