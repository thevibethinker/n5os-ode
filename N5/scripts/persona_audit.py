#!/usr/bin/env python3
"""
Persona Routing Audit Script
Validates that all internal N5OS personas have proper routing blocks.

Usage:
    python3 N5/scripts/persona_audit.py [--fix] [--json]

Options:
    --fix   Output suggested fixes for non-compliant personas
    --json  Output results as JSON for programmatic use
"""

import subprocess
import json
import sys
import re
from datetime import datetime
from pathlib import Path

# Canonical persona IDs - the source of truth
OPERATOR_ID = "90a7486f-46f9-41c9-a98c-21931fa5c5f6"

INTERNAL_PERSONAS = {
    "90a7486f-46f9-41c9-a98c-21931fa5c5f6": "Vibe Operator",
    "39309f92-3f9e-448e-81e2-f23eef5c873c": "Vibe Strategist",
    "567cc602-060b-4251-91e7-40be591b9bc3": "Vibe Builder",
    "88d70597-80f3-4b3e-90c1-da2c99da7f1f": "Vibe Teacher",
    "5cbe0dd8-9bfb-4cff-b2da-23112572a6b8": "Vibe Writer",
    "17def82c-ca82-4c03-9c98-4994e79f785a": "Vibe Debugger",
    "74e0a70d-398a-4337-bcab-3e5a3a9d805c": "Vibe Architect",
    "d0f04503-3ab4-447f-ba24-e02611993d90": "Vibe Researcher",
    "76cccdcd-2709-490a-84a3-ca67c9852a82": "Vibe Level Upper",
    "9790ca46-ae01-4ad5-b2eb-a5e72aeb22e7": "Vibe Coach",
    "1bb66f53-9e2a-4152-9b18-75c2ee2c25a3": "Vibe Librarian",
    "c545cc7a-ccbf-47ff-8c50-cb61b3c2eae3": "Vibe Trainer",
    "f25038f1-114c-4f77-8bd2-40f1ed07182d": "Vibe Nutritionist",
}

PUBLIC_FACING_MARKERS = [
    "[CE]",  # Community Edition
    "PUBLIC-FACING PERSONA",
    "DO NOT MODIFY VIA N5OS",
]

def get_personas():
    """Fetch all personas via zo ask API."""
    script = '''
import json
import os
import requests

response = requests.post(
    "https://api.zo.computer/zo/ask",
    headers={
        "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
        "content-type": "application/json"
    },
    json={
        "input": "Run list_personas and return ONLY the raw JSON array output, nothing else.",
        "output_format": {
            "type": "object",
            "properties": {
                "personas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "prompt": {"type": "string"}
                        }
                    }
                }
            }
        }
    },
    timeout=60
)
result = response.json()
print(json.dumps(result.get("output", {}).get("personas", [])))
'''
    # For now, we'll parse from a simpler approach
    return None

def check_routing_compliance(persona_id: str, persona_name: str, prompt: str) -> dict:
    """Check if a persona has proper routing instructions."""
    
    result = {
        "id": persona_id,
        "name": persona_name,
        "is_internal": persona_id in INTERNAL_PERSONAS,
        "is_public_facing": any(marker in prompt for marker in PUBLIC_FACING_MARKERS),
        "checks": {},
        "compliant": False,
        "issues": []
    }
    
    # Skip public-facing personas - they should NOT have routing
    if result["is_public_facing"]:
        result["compliant"] = True
        result["checks"]["public_facing_protected"] = True
        return result
    
    # Skip Operator - it doesn't return to itself
    if persona_id == OPERATOR_ID:
        result["compliant"] = True
        result["checks"]["is_operator"] = True
        return result
    
    # For internal personas, check required elements
    prompt_lower = prompt.lower()
    
    # Check 1: Has a Routing section
    has_routing_section = "routing" in prompt_lower and "handoff" in prompt_lower
    result["checks"]["has_routing_section"] = has_routing_section
    if not has_routing_section:
        result["issues"].append("Missing '## Routing & Handoff' section")
    
    # Check 2: Has explicit set_active_persona call
    has_set_active = "set_active_persona" in prompt
    result["checks"]["has_set_active_persona"] = has_set_active
    if not has_set_active:
        result["issues"].append("Missing set_active_persona() calls")
    
    # Check 3: Has return to Operator instruction
    return_patterns = [
        f'set_active_persona("{OPERATOR_ID}")',
        f"set_active_persona('{OPERATOR_ID}')",
        "return to operator",
    ]
    has_return = any(p.lower() in prompt.lower() for p in return_patterns)
    result["checks"]["has_return_to_operator"] = has_return
    if not has_return:
        result["issues"].append(f"Missing explicit return to Operator: set_active_persona(\"{OPERATOR_ID}\")")
    
    # Check 4: References routing contract
    has_contract_ref = "persona_routing_contract" in prompt
    result["checks"]["references_routing_contract"] = has_contract_ref
    if not has_contract_ref:
        result["issues"].append("Missing reference to N5/prefs/system/persona_routing_contract.md")
    
    # Check 5: Valid persona IDs in handoff calls
    id_pattern = r'set_active_persona\(["\']([a-f0-9-]{36})["\']\)'
    referenced_ids = re.findall(id_pattern, prompt)
    invalid_ids = [pid for pid in referenced_ids if pid not in INTERNAL_PERSONAS]
    result["checks"]["valid_persona_ids"] = len(invalid_ids) == 0
    if invalid_ids:
        result["issues"].append(f"Invalid persona IDs referenced: {invalid_ids}")
    
    # Overall compliance
    critical_checks = ["has_routing_section", "has_set_active_persona", "has_return_to_operator"]
    result["compliant"] = all(result["checks"].get(c, False) for c in critical_checks)
    
    return result

def generate_routing_block(persona_name: str) -> str:
    """Generate a standard routing block for a persona."""
    return f'''
## Routing & Handoff

**Routing contract:** `N5/prefs/system/persona_routing_contract.md`

**When to hand off:**
- Implementation needed → Builder: `set_active_persona("567cc602-060b-4251-91e7-40be591b9bc3")`
- Strategy/options needed → Strategist: `set_active_persona("39309f92-3f9e-448e-81e2-f23eef5c873c")`
- Research needed → Researcher: `set_active_persona("d0f04503-3ab4-447f-ba24-e02611993d90")`
- Documentation needed → Writer: `set_active_persona("5cbe0dd8-9bfb-4cff-b2da-23112572a6b8")`

**When work is complete:** Return to Operator: `set_active_persona("{OPERATOR_ID}")`
'''

def main():
    args = sys.argv[1:]
    show_fix = "--fix" in args
    output_json = "--json" in args
    
    print("=" * 60)
    print("PERSONA ROUTING AUDIT")
    print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    print("This script validates persona routing compliance.")
    print("Run with actual persona data by piping JSON input or")
    print("invoking from Zo with list_personas output.")
    print()
    print("Expected checks for internal personas:")
    print("  1. Has '## Routing & Handoff' section")
    print("  2. Has set_active_persona() calls")
    print("  3. Has explicit return to Operator")
    print("  4. References routing contract")
    print("  5. All referenced persona IDs are valid")
    print()
    print(f"Operator ID: {OPERATOR_ID}")
    print(f"Internal personas tracked: {len(INTERNAL_PERSONAS)}")
    print()
    
    # Check if we have stdin input
    if not sys.stdin.isatty():
        try:
            input_data = sys.stdin.read()
            personas = json.loads(input_data)
            
            results = []
            compliant_count = 0
            non_compliant = []
            
            for p in personas:
                result = check_routing_compliance(
                    p.get("id", ""),
                    p.get("name", ""),
                    p.get("prompt", "")
                )
                results.append(result)
                if result["compliant"]:
                    compliant_count += 1
                elif result["is_internal"] and not result["is_public_facing"]:
                    non_compliant.append(result)
            
            if output_json:
                print(json.dumps(results, indent=2))
            else:
                print(f"Total personas: {len(personas)}")
                print(f"Compliant: {compliant_count}")
                print(f"Non-compliant (internal): {len(non_compliant)}")
                print()
                
                if non_compliant:
                    print("NON-COMPLIANT PERSONAS:")
                    print("-" * 40)
                    for nc in non_compliant:
                        print(f"\n{nc['name']} ({nc['id'][:8]}...)")
                        for issue in nc["issues"]:
                            print(f"  ❌ {issue}")
                        
                        if show_fix:
                            print("\n  SUGGESTED FIX - Add this block:")
                            print("  " + "-" * 30)
                            fix = generate_routing_block(nc["name"])
                            for line in fix.split("\n"):
                                print(f"  {line}")
                else:
                    print("✅ All internal personas are routing-compliant!")
                    
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON input: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No input provided. Usage:")
        print("  list_personas | python3 persona_audit.py")
        print("  python3 persona_audit.py --fix < personas.json")
        print()
        print("Or invoke from Zo:")
        print('  "Run list_personas, then pipe output to persona_audit.py"')

if __name__ == "__main__":
    main()

