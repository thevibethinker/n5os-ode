---
created: 2026-02-07
last_edited: 2026-02-07
version: 1.0
provenance: con_uxJwDgh3BlXKUPsL
---

# VA API Setup Guide (Reverse Bridge)

## Overview

This guide enables zoputer to call va for guidance (the reverse of the existing bridge). The VA API key allows zoputer to send prompts to va when it encounters situations requiring higher-level strategic input or when confidence is below decision thresholds.

## Communication Model

The bidirectional setup creates two API bridges:

```
va.zo.computer                    zoputer.zo.computer
     │                                   │
     │ ←── VA_API_KEY (zoputer has) ──── │
     │                                   │
     │ ──── ZOPUTER_API_KEY (va has) ──→ │
     │                                   │

va can call zoputer                 zoputer can call va
for client work                     for guidance/oversight
```

## Step 1: Create API Key on va

1. **Navigate to va:** Go to `va.zo.computer`
2. **Access Settings:** Navigate to Settings > API & MCP 
3. **Create Key:** Click "Create New API Key"
4. **Name the Key:** Use name: `ZOPUTER_CALLBACK`
5. **Set Permissions:** Ensure full access for consultancy operations
6. **Copy Immediately:** Copy the generated key - it won't be shown again

## Step 2: Add Key to zoputer

1. **Navigate to zoputer:** Go to `zoputer.zo.computer`
2. **Access Secrets:** Navigate to Settings > Advanced > Secrets
3. **Add Secret:**
   - Name: `VA_API_KEY`
   - Value: [paste the key from Step 1]
4. **Save:** Click Save/Add Secret

## Step 3: Verify Connection

On zoputer, test the connection:

```bash
python3 N5/scripts/va_client.py ping
```

**Expected Response:**
```
✓ va responded in 0.23s
Connection: healthy
Bridge: bidirectional
```

If the command fails, see Troubleshooting below.

## When zoputer Should Call va

The reverse bridge should be activated in these scenarios:

### Confidence Threshold
- Confidence < 0.7 on any decision that affects client deliverables
- Novel situation without clear precedent in knowledge base
- Complex strategic decisions requiring V's judgment

### Structural Changes
- Any modification to core zoputer patterns or architecture
- Changes to client-facing interfaces or deliverables
- Updates to audit protocols or security measures

### Client Scenarios
- Client request that might change established workflows
- New client onboarding requiring custom configuration
- Escalation of client concerns beyond standard protocols

### Quality Assurance
- Before finalizing major deliverables (>5 hours of work)
- When multiple approaches seem viable and strategic input needed
- Error patterns that might indicate architectural issues

## Usage Pattern

When zoputer needs guidance:

```python
response = va_client.ask(
    prompt="Situation description",
    context="Relevant background",
    confidence=0.6,
    priority="high|medium|low"
)
```

va will respond with:
- Strategic guidance
- Go/no-go decisions  
- Alternative approaches
- Risk assessments

## Security Notes

### Key Management
- **Rotation Schedule:** Rotate quarterly or if compromised
- **Access Scope:** Key allows zoputer to send prompts to va
- **Audit Trail:** All communications logged to both audit databases
- **Encryption:** All API calls use TLS encryption

### Response Handling
- va responses are automatically logged to zoputer's audit system
- Responses include confidence scores for further processing
- Emergency stop: zoputer can disable bridge if va unavailable

### Privacy Controls
- zoputer will redact sensitive client data before sending
- va responses contain strategic guidance only, not client specifics
- Both sides maintain separate audit logs for transparency

## Troubleshooting

### Key Not Working
**Symptoms:** 401 Unauthorized errors
**Solutions:**
1. Check for trailing spaces when copying the key
2. Verify key was pasted correctly in zoputer secrets
3. Confirm key name is exactly `VA_API_KEY` (case sensitive)
4. Try regenerating the key on va if issue persists

### Connection Timeout
**Symptoms:** Request timeout or network errors
**Solutions:**
1. Check if va.zo.computer is running and accessible
2. Verify internet connectivity from zoputer
3. Check if firewall blocking HTTPS requests
4. Test with longer timeout values

### Invalid Response Format
**Symptoms:** Parsing errors or unexpected response structure
**Solutions:**
1. Check API version compatibility
2. Verify both systems are updated to latest versions
3. Review recent changes to va's API endpoints
4. Test with simple ping request first

### Rate Limiting
**Symptoms:** 429 Too Many Requests errors
**Solutions:**
1. Implement exponential backoff in client calls
2. Review calling frequency - should be strategic, not routine
3. Check if multiple processes calling simultaneously
4. Contact V if limits seem too restrictive

## Testing Checklist

Before considering setup complete:

- [ ] Key created successfully on va
- [ ] Key added to zoputer secrets without errors
- [ ] Ping test returns successful response
- [ ] va_client.py can make test calls
- [ ] Response format matches expected structure
- [ ] Audit logs show successful communication
- [ ] Error handling works (test with invalid key)
- [ ] Connection survives zoputer restart

## Emergency Procedures

### If Bridge Compromised
1. Immediately revoke VA_API_KEY on va
2. Generate new key with different name
3. Update zoputer secrets with new key
4. Review audit logs for suspicious activity
5. Notify V of security incident

### If va Unavailable
1. zoputer should gracefully degrade to autonomous mode
2. Queue non-critical calls for later retry
3. Escalate critical decisions to V via direct channels
4. Log all degraded operations for later review

---

*This guide enables strategic oversight while maintaining operational autonomy. The reverse bridge ensures zoputer can access va's judgment when needed while preserving the independence of both systems.*