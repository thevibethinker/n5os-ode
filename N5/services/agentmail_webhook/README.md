---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.0
provenance: con_qkaSQZCvQoQlHBTn
---

# AgentMail Webhook Receiver

Production webhook receiver for AgentMail inboxes with layered prompt-injection defenses.

## Supported Inboxes (default)
- `careerspan.n5os@agentmail.to` -> `careerspan`
- `hotline.n5os@agentmail.to` -> `hotline`
- `n5os@agentmail.to` -> `ops`

You can override mapping with `AGENTMAIL_INBOX_ROLE_MAP` JSON.

## Security Model
1. Svix signature verification (`svix-id`, `svix-timestamp`, `svix-signature`)
2. Inbox allow-map (ignore unknown inboxes)
3. Prompt-injection and adversarial pattern scan
4. Unknown sender review policy
5. Queue routing: `auto`, `review`, `quarantine`

## Output Artifacts
- Queue files: `N5/inbox/agentmail/<auto|review|quarantine>/<role>/...json`
- Audit log: `N5/logs/agentmail_webhook_audit.jsonl`
- Event DB: `N5/data/agentmail_webhooks.db`

## Environment Variables
- `AGENTMAIL_WEBHOOK_SECRET` (required in production)
- `AGENTMAIL_INBOX_ROLE_MAP` (optional JSON map)
- `AGENTMAIL_TRUSTED_SENDERS` (optional comma-separated)
- `AGENTMAIL_TRUSTED_SENDER_DOMAINS` (optional comma-separated)
- `AGENTMAIL_UNKNOWN_SENDERS_REVIEW` (default `1`)
- `AGENTMAIL_WEBHOOK_PORT` (default `8791`)
- `AGENTMAIL_ALLOW_INSECURE` (default `0`, only for local testing)

## Run Locally
```bash
cd /home/workspace
python3 -m venv N5/services/agentmail_webhook/.venv
N5/services/agentmail_webhook/.venv/bin/pip install -r N5/services/agentmail_webhook/requirements.txt
PYTHONPATH=/home/workspace/N5/services \
AGENTMAIL_WEBHOOK_SECRET=whsec_replace_me \
N5/services/agentmail_webhook/.venv/bin/python -m uvicorn agentmail_webhook.webhook_receiver:app --host 0.0.0.0 --port 8791 --app-dir /home/workspace/N5/services
```

## Register as Zo User Service
```bash
label: agentmail-webhook
protocol: http
local_port: 8791
entrypoint: python3 -m uvicorn agentmail_webhook.webhook_receiver:app --host 0.0.0.0 --port 8791
workdir: /home/workspace/N5/services
env_vars:
  PYTHONPATH: /home/workspace/N5/services
  AGENTMAIL_WEBHOOK_PORT: 8791
```

## AgentMail Console Setup
1. Create webhook URL: `https://agentmail-webhook-va.zocomputer.io/webhook/agentmail`
2. Subscribe to `message.received` (optionally `message.sent`, `message.delivered`, `message.bounced`)
3. Copy webhook secret and set `AGENTMAIL_WEBHOOK_SECRET` in Zo secrets
4. Test by emailing each inbox once

## Test
```bash
cd /home/workspace
python3 Skills/agentmail-inbox-firewall/scripts/agentmail_firewall.py test
```
