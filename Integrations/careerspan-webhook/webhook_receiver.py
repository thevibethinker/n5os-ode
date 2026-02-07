#!/usr/bin/env python3
"""
Careerspan Intelligence Brief Webhook Receiver

Receives webhook POSTs when candidates complete their Careerspan Stories.
Triggers the decompose → meta-resume → upload pipeline.

⚠️ BEFORE USE:
1. Set CAREERSPAN_WEBHOOK_SECRET in Zo secrets
2. Register this webhook URL in Careerspan admin
3. Ensure corridorx_account_id is set in pipeline config
"""

import hashlib
import hmac
import json
import os
import subprocess
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional

# Configuration
PORT = 8850
WEBHOOK_SECRET = os.environ.get("CAREERSPAN_WEBHOOK_SECRET", "")
PIPELINE_DIR = Path("/home/workspace/Integrations/careerspan-pipeline")
DECOMPOSER_SCRIPT = Path("/home/workspace/Skills/careerspan-decomposer/scripts/decompose.py")
META_RESUME_SCRIPT = Path("/home/workspace/Skills/meta-resume-generator/scripts/generate-decoded.ts")
INBOX_DIR = Path("/home/workspace/Careerspan/meta-resumes/inbox")
LOG_FILE = Path("/dev/shm/careerspan-webhook.log")


def log(message: str):
    """Log to file and stdout."""
    timestamp = datetime.now().isoformat()
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature using HMAC-SHA256."""
    if not WEBHOOK_SECRET:
        log("⚠️  No webhook secret configured - skipping signature verification")
        return True
    
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected}", signature)


def process_brief(data: dict) -> dict:
    """
    Process an Intelligence Brief through the pipeline.
    
    Steps:
    1. Download/extract brief content
    2. Run decomposer to get structured YAML
    3. Run meta-resume generator to create PDF
    4. Upload to Google Drive
    5. Return results for notification
    """
    candidate = data.get("candidate", {})
    job = data.get("job_opening", {})
    brief = data.get("brief", {})
    
    candidate_name = candidate.get("name", "unknown")
    candidate_slug = candidate_name.lower().replace(" ", "-")
    company_name = job.get("company", "unknown")
    company_slug = company_name.lower().replace(" ", "-")
    
    log(f"Processing brief for {candidate_name} → {company_name}")
    
    # Create inbox directory for this candidate
    inbox_path = INBOX_DIR / f"{candidate_slug}-{company_slug}"
    inbox_path.mkdir(parents=True, exist_ok=True)
    
    # Save raw brief data
    brief_json_path = inbox_path / "brief_payload.json"
    with open(brief_json_path, "w") as f:
        json.dump(data, f, indent=2)
    
    result = {
        "candidate": candidate_name,
        "company": company_name,
        "score": brief.get("score"),
        "inbox_path": str(inbox_path),
        "steps": []
    }
    
    # Step 1: If brief has a download URL, fetch it
    brief_url = brief.get("url")
    if brief_url:
        log(f"  → Downloading brief from {brief_url}")
        # TODO: Download brief PDF/doc
        result["steps"].append({"step": "download", "status": "pending", "url": brief_url})
    
    # Step 2: If brief has inline data, save it
    brief_data = brief.get("data")
    if brief_data:
        brief_data_path = inbox_path / "brief_data.json"
        with open(brief_data_path, "w") as f:
            json.dump(brief_data, f, indent=2)
        result["steps"].append({"step": "save_data", "status": "complete"})
    
    # Step 3: Trigger decomposer (async via /zo/ask for full processing)
    # For now, just queue it - the heartbeat or manual run will pick it up
    queue_file = PIPELINE_DIR / "queue" / f"{candidate_slug}-{company_slug}.json"
    queue_data = {
        "type": "careerspan_complete",
        "candidate": candidate,
        "job_opening": job,
        "brief": brief,
        "inbox_path": str(inbox_path),
        "received_at": datetime.now().isoformat()
    }
    with open(queue_file, "w") as f:
        json.dump(queue_data, f, indent=2)
    
    result["steps"].append({"step": "queued", "status": "complete", "queue_file": str(queue_file)})
    result["status"] = "queued_for_processing"
    
    log(f"  → Queued for processing: {queue_file}")
    
    return result


class WebhookHandler(BaseHTTPRequestHandler):
    """Handle incoming webhook requests."""
    
    def do_POST(self):
        """Process POST requests to webhook endpoint."""
        if self.path != "/webhook" and self.path != "/":
            self.send_error(404, "Not Found")
            return
        
        # Read payload
        content_length = int(self.headers.get("Content-Length", 0))
        payload = self.rfile.read(content_length)
        
        # Verify signature
        signature = self.headers.get("X-Careerspan-Signature", "")
        if not verify_signature(payload, signature):
            log("❌ Invalid signature")
            self.send_error(401, "Invalid signature")
            return
        
        # Parse JSON
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            log(f"❌ Invalid JSON: {e}")
            self.send_error(400, f"Invalid JSON: {e}")
            return
        
        # Log received event
        event_type = data.get("event", "unknown")
        log(f"📥 Received event: {event_type}")
        
        # Process based on event type
        if event_type == "brief_completed":
            result = process_brief(data)
            response = {"status": "accepted", "result": result}
        elif event_type == "ping":
            response = {"status": "pong", "timestamp": datetime.now().isoformat()}
        else:
            log(f"⚠️  Unknown event type: {event_type}")
            response = {"status": "ignored", "reason": f"Unknown event: {event_type}"}
        
        # Send response
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def do_GET(self):
        """Health check endpoint."""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "status": "healthy",
                "service": "careerspan-webhook",
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, "Not Found")
    
    def log_message(self, format, *args):
        """Suppress default logging (we have our own)."""
        pass


def main():
    """Start the webhook server."""
    if not WEBHOOK_SECRET:
        print("⚠️  WARNING: CAREERSPAN_WEBHOOK_SECRET not set")
        print("   Webhook signature verification is disabled")
        print("   Set the secret in Zo Settings > Developers > Secrets")
        print()
    
    server = HTTPServer(("0.0.0.0", PORT), WebhookHandler)
    log(f"🚀 Careerspan webhook receiver starting on port {PORT}")
    log(f"   Endpoint: POST /webhook")
    log(f"   Health: GET /health")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
