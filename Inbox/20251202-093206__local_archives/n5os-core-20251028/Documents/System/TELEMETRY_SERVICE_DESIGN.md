# N5 OS Telemetry Service — Design Spec

**Goal**: Anonymous, opt-in usage tracking to understand how N5 OS is being used

---

## Architecture Overview

### Privacy-First Principles

1. **Opt-in only** - Disabled by default, user must explicitly enable
2. **Anonymous** - No personally identifiable information
3. **Transparent** - User sees exactly what's sent before enabling
4. **Local control** - User can disable anytime, data deleted locally
5. **Minimal** - Only usage patterns, never content

---

## What Gets Tracked (If Opted In)

### ✅ Allowed (Anonymous Usage Data)

```json
{
  "installation_id": "n5_a3f7b9d2",  // Random UUID, not tied to user
  "version": "1.0-core",
  "timestamp": "2025-10-26T22:00:00Z",
  "event_type": "command_executed",
  "data": {
    "command": "index-rebuild",
    "duration_seconds": 12,
    "success": true,
    "error_type": null
  }
}
```

**Tracks**:
- Commands used (frequency, success rate)
- Scripts executed (which ones, how often)
- Workflows completed (meeting-process, list-add, etc.)
- Feature usage (personas loaded, scheduled tasks run)
- Errors encountered (types, not content)
- Install date, version, updates applied

### ❌ Never Tracked

- User names, emails, or identifiers
- File names or content
- Conversation text or summaries
- List items or knowledge base content
- API keys or credentials
- IP addresses (anonymized at collection)
- Location data

---

## Implementation: Two-Tier System

### Tier 1: Local Collection (Always)

```bash
# Local telemetry file (never leaves machine unless opted in)
N5/runtime/telemetry.jsonl

# Example entry:
{"ts": "2025-10-26T22:00:00Z", "event": "command_executed", "cmd": "index-rebuild", "duration": 12, "success": true}
```

**Purpose**: User can always see their own usage patterns

**Commands**:
```bash
# View your telemetry
python3 N5/scripts/n5_telemetry_view.py --last 7-days

# Export for debugging
python3 N5/scripts/n5_telemetry_view.py --export telemetry_export.json

# Clear local telemetry
python3 N5/scripts/n5_telemetry_view.py --clear
```

### Tier 2: Remote Reporting (Opt-In)

```bash
# Enable telemetry reporting
python3 N5/scripts/n5_telemetry_setup.py --enable

# Shows preview of what will be sent:
"""
The following anonymous data will be sent daily:
- Command usage counts (which commands, how often)
- Script execution stats (success rate, errors)
- Feature usage (personas, workflows)
- Installation ID: n5_a3f7b9d2 (random, not linked to you)

NOT sent:
- Your name, email, or any personal info
- File names or content
- Conversation text
- List items or knowledge

Send to: https://telemetry.n5os.io/v1/usage

Enable? (y/n)
"""
```

**After enabling**:
- Daily batch upload (not real-time)
- Only sends aggregated stats (not individual events)
- User can review batch before sending
- Automatically disabled if server unreachable

---

## Telemetry Server (Your Side)

### Simple Flask API

```python
# telemetry_server.py
from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/v1/usage', methods=['POST'])
def collect_usage():
    data = request.json
    
    # Validate payload
    if not validate_telemetry(data):
        return jsonify({"error": "invalid"}), 400
    
    # Strip any PII (defensive)
    sanitized = sanitize_payload(data)
    
    # Store
    with open('telemetry.jsonl', 'a') as f:
        f.write(json.dumps({
            **sanitized,
            'received_at': datetime.utcnow().isoformat(),
            'ip': None  # Don't log IPs
        }) + '\n')
    
    return jsonify({"status": "ok"}), 200

def validate_telemetry(data):
    required = ['installation_id', 'version', 'events']
    return all(k in data for k in required)

def sanitize_payload(data):
    # Remove any fields that shouldn't be there
    allowed = {'installation_id', 'version', 'events', 'timestamp'}
    return {k: v for k, v in data.items() if k in allowed}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
```

### Deploy Options

**Option A: Simple (Recommended for MVP)**
- Deploy Flask app on your Zo instance
- Use register_user_service to keep it running
- URL: `https://va.zo.computer/telemetry/v1/usage`

**Option B: External Service**
- Deploy to Vercel/Railway/Fly.io
- Use database (Postgres/MongoDB) for storage
- Add analytics dashboard

---

## Dashboard Queries

### Most Used Commands

```bash
# Query telemetry.jsonl
cat telemetry.jsonl | jq -r 'select(.events[].event_type == "command_executed") | .events[].data.command' | sort | uniq -c | sort -rn | head -10
```

### Success Rates

```bash
# Command success rate
cat telemetry.jsonl | jq -r '.events[] | select(.event_type == "command_executed") | "\(.data.command) \(.data.success)"' | awk '{cmds[$1]++; if($2=="true") success[$1]++} END {for(c in cmds) printf "%s: %.1f%% (%d/%d)\n", c, (success[c]/cmds[c])*100, success[c], cmds[c]}' | sort -t: -k2 -rn
```

### Active Installations

```bash
# Unique installations reporting this week
cat telemetry.jsonl | jq -r 'select(.timestamp > "2025-10-20") | .installation_id' | sort -u | wc -l
```

### Feature Adoption

```bash
# How many users use each feature
cat telemetry.jsonl | jq -r '.events[] | select(.event_type == "feature_used") | .data.feature' | sort | uniq -c | sort -rn
```

---

## User Experience

### First Run (During Onboarding)

```
[Step 11/12] Telemetry (Optional)

N5 OS can send anonymous usage data to help improve the system.

What's collected:
✓ Command usage (which commands, how often)
✓ Error types (not content)
✓ Feature usage patterns

What's NOT collected:
✗ Your name, email, or personal info
✗ File names or content
✗ Conversation text
✗ Anything in your lists or knowledge base

You can:
- View what's sent before it's sent
- Disable anytime
- Export your data
- Clear all telemetry data

Enable anonymous telemetry? (y/n) [default: n]:
```

### Reviewing Before Send

```bash
# User can review daily batch
python3 N5/scripts/n5_telemetry_review.py

"""
Daily telemetry report (ready to send):

Commands used today:
- index-rebuild: 3 times (100% success)
- git-check: 1 time (100% success)
- conversation-end: 2 times (100% success)

Features used:
- Vibe Builder persona: 1 time

Errors: None

Installation ID: n5_a3f7b9d2
Version: 1.0-core

Send this report? (y/n/never):
  y - Send now
  n - Skip today
  never - Disable telemetry
"""
```

---

## Privacy Guarantees

### Technical Measures

1. **No cookies** - No tracking cookies or browser fingerprinting
2. **No IP logging** - IPs not stored on server
3. **Anonymized ID** - Random UUID, not tied to user
4. **Aggregation only** - Individual events aggregated before sending
5. **Local-first** - All telemetry stored locally, opt-in to sync

### Legal Compliance

- **GDPR compliant** - Anonymous data, user control
- **CCPA compliant** - No personal data sold or shared
- **Transparent** - Full disclosure in LICENSE and docs

---

## Integration with Onboarding

In `onboarding.py` (Step 11):

```python
def step_telemetry():
    print("\n[Step 11/12] Anonymous Telemetry (Optional)\n")
    print("Help improve N5 OS by sharing anonymous usage data.")
    print("\nCollected: Command usage, error types, feature usage")
    print("NOT collected: Personal info, file content, conversations")
    print("\nFull details: file 'TELEMETRY_SERVICE_DESIGN.md'")
    
    choice = input("\nEnable anonymous telemetry? (y/n) [default: n]: ").strip().lower()
    
    if choice == 'y':
        install_id = generate_install_id()
        config['telemetry'] = {
            'enabled': True,
            'installation_id': install_id,
            'endpoint': 'https://va.zo.computer/telemetry/v1/usage',
            'frequency': 'daily',
            'review_before_send': True
        }
        print(f"✓ Telemetry enabled (ID: {install_id})")
        print("  You can disable anytime: python3 N5/scripts/n5_telemetry_setup.py --disable")
    else:
        config['telemetry'] = {'enabled': False}
        print("✓ Telemetry disabled")
```

---

## Commands Reference

### For Users

```bash
# Check telemetry status
python3 N5/scripts/n5_telemetry_setup.py --status

# Enable telemetry
python3 N5/scripts/n5_telemetry_setup.py --enable

# Disable telemetry
python3 N5/scripts/n5_telemetry_setup.py --disable

# View local telemetry
python3 N5/scripts/n5_telemetry_view.py --last 30-days

# Export for debugging
python3 N5/scripts/n5_telemetry_view.py --export my_usage.json

# Clear all telemetry data
python3 N5/scripts/n5_telemetry_view.py --clear --confirm
```

### For You (Consultant)

```bash
# Deploy telemetry server
python3 telemetry_server.py

# Query usage patterns
./query_telemetry.sh most-used-commands
./query_telemetry.sh success-rates
./query_telemetry.sh active-installations
./query_telemetry.sh feature-adoption

# Export for analysis
./export_telemetry.sh --format csv --output n5_usage_report.csv
```

---

## Rollout Plan

### Phase 1 (v1.1): Local Only
- Implement local telemetry collection
- User can view their own usage
- No remote reporting yet

### Phase 2 (v1.2): Opt-In Remote
- Deploy telemetry server
- Add opt-in during onboarding
- Daily batch uploads
- Simple dashboard for you

### Phase 3 (v1.3): Analytics
- Advanced dashboard
- Usage trends over time
- Feature adoption funnel
- Error analytics

---

**Version**: 1.0 (Design)  
**Status**: Ready for v1.2 implementation  
**Privacy**: Opt-in, anonymous, transparent  
**Date**: 2025-10-26
