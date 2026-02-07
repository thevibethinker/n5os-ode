#!/usr/bin/env python3

import argparse
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Tuple

sys.path.insert(0, '/home/workspace/Integrations/calendly-zoffice/scripts')
from session_prep import handle_invitee_created, handle_invitee_canceled

sys.path.insert(0, '/home/workspace/Skills/audit-system/scripts')
from audit_logger import log_entry


def _parse_signature_header(header_val: str) -> Tuple[str, str]:
    """Returns (t, v1)."""
    t, v1 = '', ''
    for part in (header_val or '').split(','):
        part = part.strip()
        if not part or '=' not in part:
            continue
        k, v = part.split('=', 1)
        if k == 't':
            t = v
        elif k == 'v1':
            v1 = v
    return t, v1


def verify_calendly_signature(body: bytes, signature_header: str, signing_key: str) -> bool:
    if not signing_key:
        # No key configured; treat as verified.
        return True

    t, v1 = _parse_signature_header(signature_header)
    if not t or not v1:
        return False

    msg = t.encode() + b'.' + body
    expected = hmac.new(signing_key.encode(), msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, v1)


def process_event(event: dict) -> dict:
    et = event.get('event') or event.get('event_type') or ''

    if et == 'invitee.created':
        return handle_invitee_created(event)
    if et == 'invitee.canceled':
        return handle_invitee_canceled(event)

    # Legacy placeholder payload (D2.3)
    if event.get('event_type') and event.get('start_time'):
        # Treat as a booking
        legacy = {
            "event": "invitee.created",
            "payload": {
                "name": event.get('invitee', {}).get('name') or 'Unknown',
                "email": event.get('invitee', {}).get('email'),
                "event_type": {"name": event.get('event_type')},
                "scheduled_event": {"start_time": event.get('start_time')},
            }
        }
        return handle_invitee_created(legacy)

    return {"status": "ignored", "reason": f"Unhandled event type: {et or 'unknown'}"}


class CalendlyWebhookHandler(BaseHTTPRequestHandler):
    signing_key: str = ''

    def do_POST(self):
        if self.path not in ('/api/calendly/webhook', '/webhook', '/'): 
            self.send_error(404, 'Not Found')
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        sig = self.headers.get('Calendly-Webhook-Signature', '')
        verified = verify_calendly_signature(body, sig, self.signing_key)
        if not verified:
            log_entry(
                entry_type='calendly_webhook_rejected',
                direction='calendly-to-zoputer',
                payload=body.decode('utf-8', errors='replace')[:20000],
                metadata={"reason": "invalid_signature"}
            )
            self.send_error(401, 'Invalid signature')
            return

        try:
            event = json.loads(body)
        except json.JSONDecodeError as e:
            self.send_error(400, f'Invalid JSON: {e}')
            return

        log_entry(
            entry_type='calendly_webhook_received',
            direction='calendly-to-zoputer',
            payload=json.dumps({"event": event.get('event'), "received_at": datetime.utcnow().isoformat()}),
            metadata={"path": self.path}
        )

        result = process_event(event)

        out = json.dumps({"ok": True, "result": result}).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(out)

    def do_GET(self):
        if self.path == '/health':
            out = json.dumps({"status": "healthy", "service": "calendly-zoffice"}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(out)
        else:
            self.send_error(404, 'Not Found')

    def log_message(self, format, *args):
        # Suppress default server logging
        pass


def serve(port: int, signing_key: str) -> None:
    CalendlyWebhookHandler.signing_key = signing_key
    server = HTTPServer(('0.0.0.0', port), CalendlyWebhookHandler)
    print(f"Calendly webhook server listening on :{port}")
    print("POST /api/calendly/webhook  (also accepts /webhook)")
    print("GET  /health")
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description='Calendly webhook handler for Zoffice')
    parser.add_argument('--stdin', action='store_true', help='Read a single JSON payload from stdin (skips signature verification)')

    sub = parser.add_subparsers(dest='cmd')
    serve_p = sub.add_parser('serve', help='Run HTTP server')
    serve_p.add_argument('--port', type=int, default=int(os.environ.get('PORT', '8851')))

    args = parser.parse_args()

    signing_key = (os.environ.get('CALENDLY_WEBHOOK_SIGNING_KEY') or '').strip()

    if args.stdin:
        raw = sys.stdin.read()
        if not raw.strip():
            print(json.dumps({"ok": False, "error": "No stdin provided"}))
            sys.exit(1)
        event = json.loads(raw)
        result = process_event(event)
        print(json.dumps({"ok": True, "result": result}, indent=2))
        return

    if args.cmd == 'serve':
        serve(args.port, signing_key)
        return

    parser.print_help()


if __name__ == '__main__':
    main()
