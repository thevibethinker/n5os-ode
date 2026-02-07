---
name: security-gate
description: Client-facing security scanner for the Zoffice Consultancy Stack. Detects prompt injection, adversarial patterns, and social engineering attempts in inbound communications.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0"
  created: "2026-02-06"
created: 2026-02-06
last_edited: 2026-02-06
version: 1.0
provenance: con_GwlFHPrBi5KsNm1X
---
# Security Gate

## Purpose

First-line defense for the Zoffice Consultancy Stack. Scans all client inbound communications for adversarial patterns before processing.

## Usage

```bash
# Scan a message
python3 Skills/security-gate/scripts/security_scanner.py --message "message text" --sender client@example.com

# Scan from file
python3 Skills/security-gate/scripts/security_scanner.py --file /path/to/email.txt --sender client@example.com

# Run test suite
python3 Skills/security-gate/scripts/security_scanner.py --test

# JSON output for integration
python3 Skills/security-gate/scripts/security_scanner.py --message "text" --json
```

## Risk Levels

| Level | Action | Description |
|-------|--------|-------------|
| **critical** | BLOCK_AND_ALERT | Immediate escalation to V |
| **high** | QUARANTINE_AND_REVIEW | Hold for manual review |
| **medium** | LOG_AND_MONITOR | Log and continue |
| **low** | LOG_AND_PROCEED | Log and continue |
| **safe** | PROCEED | Normal processing |

## Integration

The security gate should be invoked on ALL inbound client communications before any processing:

```python
import subprocess
import json

result = subprocess.run(
    ["python3", "Skills/security-gate/scripts/security_scanner.py", 
     "--message", email_body, "--sender", sender_email, "--json"],
    capture_output=True, text=True
)

scan_result = json.loads(result.stdout)
if not scan_result["safe"]:
    # Escalate to V or quarantine
    handle_security_alert(scan_result)
```

## Patterns Detected

- **Critical**: Ignore previous instructions, new instruction injection, system prompt extraction
- **High**: Role override, encoding evasion, delimiter manipulation, false authority claims
- **Medium**: File system probing, credential requests, environment variable access
- **Low**: Urgency pressure, authority appeals (social engineering indicators)

## Whitelist

Legitimate consulting patterns are whitelisted to reduce false positives:
- "Help me set up..."
- "How do I implement..."
- "Can you advise/guide..."

## Exit Codes

- `0`: Message is safe (proceed)
- `1`: Message failed security check (block/quarantine)
