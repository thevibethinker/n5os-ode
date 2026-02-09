---
name: mentor-escalation
description: Confidence-based decision escalation system enabling zoputer to request guidance from va when facing uncertain situations. Implements mentor-apprentice relationship with structured escalation protocols.
compatibility: Created for Zo Computer
created: 2026-02-07
last_edited: 2026-02-07
version: 1.0
provenance: con_O55xMh88AODvRDLP
metadata:
  author: va.zo.computer
  skill_version: "1.0"
  created: "2026-02-07"
  build: "zoputer-autonomy-v2"
  drop: "D2.2"
---

# Mentor Escalation

## Purpose

Enables zoputer to escalate uncertain decisions to va for guidance, implementing the mentor-apprentice relationship. Uses confidence-based thresholds to determine when autonomous action is appropriate vs. when guidance is needed.

## Architecture

Based on the localization protocol decision framework:

- **>= 0.7 confidence**: Auto-decide (zoputer acts autonomously)
- **0.5-0.7 confidence**: Ask va (mentor guidance) 
- **< 0.5 confidence**: Ask V (human escalation)

## Usage

### Basic Workflow

```bash
# Assess confidence for a decision
python3 Skills/mentor-escalation/scripts/escalate.py assess "Should I modify workflow X for client Y?"

# Ask va for guidance  
python3 Skills/mentor-escalation/scripts/escalate.py ask-va "How should I handle this request?" \
  --context '{"client": "startup_a", "workflow": "hiring"}'

# Check escalation path
python3 Skills/mentor-escalation/scripts/escalate.py should-escalate --confidence 0.6
```

### Direct VA Communication

```bash
# Test va connectivity
python3 Skills/mentor-escalation/scripts/va_client.py ping

# Ask va a question directly
python3 Skills/mentor-escalation/scripts/va_client.py ask "What's the best approach for X?"

# Send structured escalation  
python3 Skills/mentor-escalation/scripts/va_client.py escalate \
  --question "Client wants to remove review gate" \
  --confidence 0.6 \
  --context '{"client": "example", "risk": "medium"}'
```

## Integration

This skill integrates with:

1. **Audit System** - All escalations logged for transparency
2. **VA API Bridge** - Bidirectional communication with va.zo.computer  
3. **Localization Protocol** - Decision framework based on established thresholds

### Prerequisites

- `VA_API_KEY` environment variable configured (see Documents/consulting/va-api-setup-guide.md)
- Audit system skill available for logging
- Network access to va.zo.computer

## Decision Framework

### Confidence Assessment Criteria

The LLM-based confidence assessor considers:

1. **Change Type**
   - Cosmetic (labels, ordering) → High confidence
   - Structural (workflow steps, dependencies) → Lower confidence

2. **Risk Level**  
   - Reversible, low client impact → Higher confidence
   - Security, audit, compliance impact → Lower confidence

3. **Precedent**
   - Clear precedent exists → Higher confidence
   - Novel situation → Lower confidence

4. **Authority Level**
   - Within established scope → Higher confidence  
   - Policy/strategic decision → Lower confidence

### Always Human Types

These decision types always escalate to V regardless of confidence:

- `security_gate_change`
- `audit_protocol_change` 
- `new_obligations`
- `legal_compliance`
- `privacy_policy_change`
- `tier_boundary_change`

## Escalation Request Format

```json
{
  "type": "mentor_escalation",
  "from": "zoputer",
  "confidence": 0.6,
  "situation": "Client asked to remove review gate from workflow",
  "context": {
    "client": "example_client",
    "current_workflow": "...",
    "requested_change": "..."
  },
  "question": "Which option should I recommend?",
  "correlation_id": "uuid",
  "timestamp": "2026-02-07T19:40:00Z"
}
```

## Response Format

va responds with structured mentoring guidance:

```json
{
  "type": "mentor_response", 
  "from": "va",
  "recommendation": "Specific action to take",
  "rationale": "Why this approach is best",
  "precedent_set": true,
  "learning_summary": "Pattern for future similar decisions"
}
```

## Error Handling

- **API failures**: Retries with exponential backoff
- **Authentication errors**: Clear setup guidance provided
- **Confidence assessment failures**: Defaults to asking va (0.6)
- **Network issues**: Graceful degradation with local logging

## Security

- All communications encrypted via HTTPS
- API keys managed through Zo's secure secrets system
- Full audit trail maintained on both va and zoputer sides
- Correlation IDs enable cross-instance verification

## Scripts

### escalate.py

Main decision framework implementation:
- `assess` - LLM-based confidence assessment
- `ask-va` - Escalate to va for guidance
- `ask-human` - Escalate to V (placeholder for D3.x)
- `should-escalate` - Check escalation path for confidence level

### va_client.py  

Direct communication client:
- `ping` - Test va connectivity
- `ask` - Send question to va
- `escalate` - Send structured escalation request

## Monitoring

All escalations are logged to the audit system with:
- Entry type: `mentor_escalation` / `mentor_response`
- Direction: `zoputer-to-va` / `va-to-zoputer`
- Correlation ID for linking requests/responses
- Full payload for audit trail

## Future Enhancements (D3.x)

- Human escalation queue integration
- SMS notification system for urgent escalations
- Learning pattern extraction from va responses
- Automatic confidence threshold tuning based on success rates

## Testing

```bash
# Test basic connectivity
python3 Skills/mentor-escalation/scripts/va_client.py ping

# Test confidence assessment
python3 Skills/mentor-escalation/scripts/escalate.py assess "Simple label change"

# Test full escalation flow
python3 Skills/mentor-escalation/scripts/escalate.py ask-va "Test question"
```