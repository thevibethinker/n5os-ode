# Zo2Zo Capability

**Status:** active

Interoffice communication layer enabling trust verification between Zo instances, parent escalation protocol, and skill bundle reception.

## Components

- `trust/registry.py` — Trust verification against security.yaml
- `protocols/parent_link.py` — Parent escalation protocol
- `protocols/skill_receiver.py` — Skill bundle validation and (dry-run) install
- `config.yaml` — Parent instance, escalation timeout, skill settings

## API Surface

### Trust Registry

```python
from Zoffice.capabilities.zo2zo.trust.registry import verify_trust, list_trusted

result = verify_trust("instance.zo.computer") -> {"trusted": bool, "level": str, "instance": str}
instances = list_trusted() -> list[str]
```

### Parent Link

```python
from Zoffice.capabilities.zo2zo.protocols.parent_link import prepare_escalation, parse_response

req = prepare_escalation(summary, context=None, options=None) -> EscalationRequest dict
resolution = parse_response(text) -> dict
```

### Skill Receiver

```python
from Zoffice.capabilities.zo2zo.protocols.skill_receiver import validate_bundle, install_bundle

result = validate_bundle(bundle) -> {"valid": bool, "issues": list}
result = install_bundle(bundle, dry_run=True) -> InstallResult dict
```
