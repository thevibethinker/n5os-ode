import json
import os
import requests
import asyncio
import aiohttp

async def run_gmail_search(email_address, query):
    prompt = f"""
Use tool gmail-find-email with the following parameters:
configured_props: {{
    "q": "{query}",
    "maxResults": 50,
    "withTextPayload": true
}}
email: "{email_address}"

Respond ONLY with the raw JSON array of message objects found. No preamble or markdown fences.
If no messages are found, respond with [].
"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://api.zo.computer/zo/ask',
            headers={
                'authorization': os.environ['ZO_CLIENT_IDENTITY_TOKEN'],
                'content-type': 'application/json'
            },
            json={'input': prompt}
        ) as resp:
            data = await resp.json()
            output = data.get('output', '[]')
            try:
                # Clean up output in case it has markdown fences
                output = output.strip()
                if output.startswith('```json'):
                    output = output[7:].strip()
                if output.startswith('```'):
                    output = output[3:].strip()
                if output.endswith('```'):
                    output = output[:-3].strip()
                return json.loads(output)
            except Exception as e:
                print(f"Error parsing JSON from {email_address}: {e}")
                print(f"Raw output: {output}")
                return []

async def main():
    query = 'from:(hi@theagentic.ai OR newsletter@marvin.vc OR events@nextplay.so) newer_than:2d'
    emails = ['attawar.v@gmail.com', 'vrijen@mycareerspan.com']
    
    results = await asyncio.gather(*[run_gmail_search(e, query) for e in emails])
    
    all_messages = []
    seen_ids = set()
    for res in results:
        if not isinstance(res, list):
            continue
        for msg in res:
            if isinstance(msg, dict) and 'id' in msg:
                if msg['id'] not in seen_ids:
                    all_messages.append(msg)
                    seen_ids.add(msg['id'])
                
    os.makedirs('N5/data', exist_ok=True)
    with open('N5/data/pending_allowlist.json', 'w') as f:
        json.dump(all_messages, f, indent=2)
    
    print(f'Total messages found and saved: {len(all_messages)}')

if __name__ == '__main__':
    asyncio.run(main())
