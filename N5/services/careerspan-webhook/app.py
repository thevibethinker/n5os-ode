from fastapi import FastAPI, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import json
import os
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INBOX_DIR = '/home/workspace/N5/inbox/careerspan-webhooks'
AUDIT_LOG = '/home/workspace/N5/logs/careerspan_webhook_audit.jsonl'
FOUNDER_TOKEN = os.environ.get('FOUNDER_AUTH_TOKEN')

os.makedirs(INBOX_DIR, exist_ok=True)
os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)

@app.get("/health")
async def health():
    return {"status": "active", "auth_required": bool(FOUNDER_TOKEN), "inbox": INBOX_DIR}

@app.post("/webhook")
async def webhook(request: Request, authorization: Optional[str] = Header(None)):
    # Auth check
    if FOUNDER_TOKEN:
        token = (authorization or "").replace("Bearer ", "")
        if token != FOUNDER_TOKEN:
            return {"error": "Unauthorized"}, 401
    
    body = await request.json()
    headers = dict(request.headers)
    
    # Save
    ts = datetime.now().isoformat().replace(":", "-").replace(".", "-")
    filename = f"{ts}.json"
    filepath = f"{INBOX_DIR}/{filename}"
    
    with open(filepath, 'w') as f:
        json.dump({"received_at": datetime.now().isoformat(), "headers": headers, "payload": body}, f, indent=2)
    
    # Audit
    with open(AUDIT_LOG, 'a') as f:
        f.write(json.dumps({"event": "webhook_received", "filename": filename, "logged_at": datetime.now().isoformat()}) + "\n")
    
    # SMS notify via Zo
    zo_token = os.environ.get('ZO_CLIENT_IDENTITY_TOKEN')
    if zo_token:
        import httpx
        summary = body.get('message') or body.get('type') or body.get('event') or f"New data ({', '.join(body.keys())})"
        try:
            httpx.post('https://api.zo.computer/zo/ask',
                headers={'Authorization': zo_token, 'Content-Type': 'application/json'},
                json={'input': f'Send SMS to V: "🔔 Careerspan webhook: {summary}". Use send_sms_to_user immediately.'},
                timeout=10)
        except: pass
    
    return {"status": "received", "filename": filename}
