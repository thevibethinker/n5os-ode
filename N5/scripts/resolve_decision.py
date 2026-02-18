#!/usr/bin/env python3
"""
Cross-Thread Resolution Handler

Enables V to resolve pending decisions from ANY conversation thread,
with the resolution routed back to the originating context.

Created by D3.3 Drop for zoputer-autonomy-v2 build.

Usage:
    python3 N5/scripts/resolve_decision.py show <decision_id>
    python3 N5/scripts/resolve_decision.py resolve <decision_id> --choice "A" --notes "..."
    python3 N5/scripts/resolve_decision.py route <decision_id>
    python3 N5/scripts/resolve_decision.py from-sms "<message>"

SMS patterns handled:
    n5 decision <id>           - View decision details
    n5 decision <id> <choice>  - Apply resolution
    n5 decision <id> A/B/C     - Choose option by letter
    n5 decision <id> custom: X - Custom instruction
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Import pending_decisions store
sys.path.insert(0, str(Path(__file__).parent))
import pending_decisions

# zoputer_client path
ZOPUTER_CLIENT = Path(__file__).parent / "zoputer_client.py"

# Audit log path
AUDIT_LOG = Path("/home/workspace/N5/logs/decision_resolutions.jsonl")


def log_resolution_audit(decision_id: str, action: str, result: dict) -> None:
    """Log resolution actions to audit trail."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "decision_id": decision_id,
        "action": action,
        "result": result
    }
    
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def show_decision_context(decision_id: str) -> str:
    """
    Format the full decision context for display.
    
    Returns a markdown-formatted string with:
    - Question
    - Background
    - Options (if any)
    - Recommendation
    - How to respond
    """
    # Support short IDs (first 8 chars)
    decision = find_decision_by_id(decision_id)
    
    if not decision:
        # List pending decisions to help user
        pending = pending_decisions.list_pending(status="pending")
        if not pending:
            return f"❌ Decision '{decision_id}' not found. No pending decisions."
        
        short_ids = [d['id'][:8] for d in pending[:5]]
        return f"❌ Decision '{decision_id}' not found.\n\nCurrent pending: {', '.join(short_ids)}"
    
    # Check if already resolved
    if decision['status'] == 'resolved':
        return (
            f"✅ Decision {decision_id[:8]} was already resolved.\n"
            f"Resolved: {decision.get('resolved_at', 'unknown')}\n"
            f"Resolution: {decision.get('resolution', 'N/A')}"
        )
    
    if decision['status'] == 'expired':
        return (
            f"⏰ Decision {decision_id[:8]} has expired.\n"
            f"Expired: {decision.get('expires_at', 'unknown')}\n"
            "Create a new decision if still needed."
        )
    
    # Format the context
    context = decision.get('full_context', {})
    short_id = decision['id'][:8]
    
    lines = [
        f"📋 Decision {short_id}",
        f"Priority: {decision['priority'].upper()}",
        f"Origin: {decision['origin']}",
        "",
        f"**Question:** {context.get('question', decision.get('summary', 'N/A'))}",
        ""
    ]
    
    if context.get('background'):
        lines.append(f"**Background:** {context['background']}")
        lines.append("")
    
    options = context.get('options') or decision.get('options')
    if options:
        lines.append("**Options:**")
        for i, opt in enumerate(options):
            letter = chr(65 + i)  # A, B, C, ...
            if isinstance(opt, dict):
                desc = opt.get('description', opt.get('label', str(opt)))
                risk = f" ⚠️ {opt.get('risk')}" if opt.get('risk') else ""
            else:
                desc = str(opt)
                risk = ""
            lines.append(f"{letter}) {desc}{risk}")
        lines.append("")
    
    if context.get('recommendation'):
        conf = context.get('recommendation_confidence')
        conf_str = f" (confidence: {conf})" if conf else ""
        lines.append(f"**Recommendation:** {context['recommendation']}{conf_str}")
        lines.append("")
    
    # Reply instructions
    lines.append("**Reply with:**")
    if options:
        for i in range(len(options)):
            letter = chr(65 + i)
            lines.append(f'- "n5 decision {short_id} {letter}" to choose option {letter}')
    lines.append(f'- "n5 decision {short_id} approve" to approve')
    lines.append(f'- "n5 decision {short_id} reject" to reject')
    lines.append(f'- "n5 decision {short_id} custom: <your instruction>" for custom response')
    
    return "\n".join(lines)


def find_decision_by_id(decision_id: str) -> Optional[Dict[str, Any]]:
    """Find a decision by full or partial ID."""
    # Try exact match first
    decision = pending_decisions.get_decision(decision_id)
    if decision:
        return decision
    
    # Try partial match (short ID)
    all_decisions = pending_decisions.list_pending(status="pending")
    # Also check resolved/expired for viewing
    all_decisions.extend(pending_decisions.list_pending(status="resolved"))
    all_decisions.extend(pending_decisions.list_pending(status="expired"))
    
    matches = [d for d in all_decisions if d['id'].startswith(decision_id)]
    
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        return None  # Ambiguous
    
    return None


def apply_resolution(
    decision_id: str,
    resolution: str,
    resolved_by_convo: str,
    notes: Optional[str] = None
) -> dict:
    """
    Apply a resolution and notify the origin.
    
    1. Update pending_decisions store
    2. If origin is zoputer: call zoputer with resolution
    3. If origin is va: update internal state
    4. Log to audit
    
    Returns:
        {"success": bool, "routed_to": str, "message": str}
    """
    # Find the decision
    decision = find_decision_by_id(decision_id)
    if not decision:
        return {
            "success": False,
            "routed_to": None,
            "message": f"Decision '{decision_id}' not found."
        }
    
    full_id = decision['id']
    
    # Check status
    if decision['status'] != 'pending':
        return {
            "success": False,
            "routed_to": None,
            "message": f"Decision already {decision['status']}."
        }
    
    # Resolve in the store
    success = pending_decisions.resolve_decision(
        decision_id=full_id,
        resolution=resolution,
        resolved_by=resolved_by_convo,
        notes=notes
    )
    
    if not success:
        return {
            "success": False,
            "routed_to": None,
            "message": "Failed to update decision store."
        }
    
    # Log to audit
    log_resolution_audit(full_id, "resolved", {
        "resolution": resolution,
        "notes": notes,
        "resolved_by": resolved_by_convo
    })
    
    # Route back to origin
    origin = decision['origin']
    route_result = route_to_origin(decision, resolution, notes)
    
    return {
        "success": True,
        "routed_to": origin,
        "message": f"✅ Decision {full_id[:8]} resolved → {origin}",
        "route_success": route_result
    }


def route_to_origin(decision: dict, resolution: str, notes: Optional[str] = None) -> bool:
    """
    Send the resolution back to the originating Zo.
    
    If origin == "zoputer":
        Use zoputer_client.py to send resolution
    If origin == "va":
        Just update local state (already done)
    """
    origin = decision['origin']
    decision_id = decision['id']
    
    if origin == "va":
        # Local resolution - nothing more to do
        log_resolution_audit(decision_id, "routed", {"target": "va", "status": "local"})
        return True
    
    if origin == "zoputer":
        # Need to call zoputer with the resolution via Python import
        try:
            import zoputer_client
            
            context = decision.get('full_context', {})
            
            prompt = f"""A decision you escalated has been resolved by V.

Decision ID: {decision_id}
Original Question: {context.get('question', decision.get('summary', 'N/A'))}
Resolution: {resolution}
Notes: {notes or 'None'}

Please:
1. Acknowledge receipt
2. Apply this guidance to the pending situation
3. Log this as a learning if applicable

Respond with a JSON confirmation:
{{"acknowledged": true, "decision_id": "{decision_id}", "action_taken": "<brief description>"}}
"""
            
            result = zoputer_client.call_zoputer(prompt, correlation_id=decision_id)
            
            log_resolution_audit(decision_id, "routed", {
                "target": "zoputer",
                "status": "success",
                "output": str(result.get('output', ''))[:500]
            })
            return True
            
        except ImportError:
            log_resolution_audit(decision_id, "route_failed", {
                "target": "zoputer",
                "error": "zoputer_client module not importable"
            })
            return False
        except Exception as e:
            log_resolution_audit(decision_id, "route_failed", {
                "target": "zoputer",
                "error": str(e)
            })
            return False
    
    # Unknown origin
    log_resolution_audit(decision_id, "route_failed", {
        "target": origin,
        "error": "unknown origin type"
    })
    return False


def resolve_from_sms(message: str, current_convo_id: str) -> dict:
    """
    Parse an SMS response and resolve the decision.
    
    Expected formats:
    - "n5 decision d7f3" - View decision details
    - "n5 decision d7f3 approve" - Quick resolution
    - "n5 decision d7f3 A" - Choose option A
    - "n5 decision d7f3 reject" - Quick rejection
    - "n5 decision d7f3 custom: <instruction>" - Custom response
    
    Returns:
        {"success": bool, "decision": dict, "action": str, "message": str}
    """
    # Normalize message
    msg = message.strip().lower()
    
    # Pattern: n5 decision <id> [choice]
    pattern = r'n5\s+decision\s+([a-f0-9]{4,36})\s*(.*)?'
    match = re.match(pattern, msg, re.IGNORECASE)
    
    if not match:
        return {
            "success": False,
            "decision": None,
            "action": "parse_error",
            "message": "Could not parse decision command. Use: n5 decision <id> [choice]"
        }
    
    decision_id = match.group(1)
    choice_raw = (match.group(2) or "").strip()
    
    # Find the decision
    decision = find_decision_by_id(decision_id)
    if not decision:
        pending = pending_decisions.list_pending(status="pending")
        if not pending:
            return {
                "success": False,
                "decision": None,
                "action": "not_found",
                "message": f"Decision '{decision_id}' not found. No pending decisions."
            }
        short_ids = [d['id'][:8] for d in pending[:5]]
        return {
            "success": False,
            "decision": None,
            "action": "not_found",
            "message": f"Decision '{decision_id}' not found.\nPending: {', '.join(short_ids)}"
        }
    
    # No choice provided - show context
    if not choice_raw:
        context_display = show_decision_context(decision_id)
        return {
            "success": True,
            "decision": decision,
            "action": "show",
            "message": context_display
        }
    
    # Already resolved?
    if decision['status'] != 'pending':
        return {
            "success": False,
            "decision": decision,
            "action": "already_resolved",
            "message": f"Decision already {decision['status']}."
        }
    
    # Parse the choice
    choice = choice_raw.upper()
    context = decision.get('full_context', {})
    options = context.get('options') or decision.get('options') or []
    
    # Single letter option (A, B, C, ...)
    if len(choice) == 1 and choice.isalpha():
        idx = ord(choice) - 65  # A=0, B=1, etc.
        if 0 <= idx < len(options):
            opt = options[idx]
            resolution = opt.get('description', opt.get('label', str(opt))) if isinstance(opt, dict) else str(opt)
            result = apply_resolution(decision['id'], f"Option {choice}: {resolution}", current_convo_id)
            return {
                "success": result['success'],
                "decision": decision,
                "action": f"option_{choice.lower()}",
                "message": result['message']
            }
        else:
            return {
                "success": False,
                "decision": decision,
                "action": "invalid_option",
                "message": f"Invalid option '{choice}'. Available: A-{chr(64+len(options))}" if options else "No options defined."
            }
    
    # Quick keywords
    if choice in ['approve', 'approved', 'yes', 'ok', 'proceed']:
        result = apply_resolution(decision['id'], "Approved", current_convo_id)
        return {
            "success": result['success'],
            "decision": decision,
            "action": "approve",
            "message": result['message']
        }
    
    if choice in ['reject', 'rejected', 'no', 'deny', 'denied', 'stop']:
        result = apply_resolution(decision['id'], "Rejected", current_convo_id)
        return {
            "success": result['success'],
            "decision": decision,
            "action": "reject",
            "message": result['message']
        }
    
    # Custom response: "custom: <instruction>"
    if choice_raw.lower().startswith('custom:'):
        custom_instruction = choice_raw[7:].strip()
        if not custom_instruction:
            return {
                "success": False,
                "decision": decision,
                "action": "custom_empty",
                "message": "Custom instruction cannot be empty."
            }
        result = apply_resolution(decision['id'], f"Custom: {custom_instruction}", current_convo_id, notes="Via SMS custom response")
        return {
            "success": result['success'],
            "decision": decision,
            "action": "custom",
            "message": result['message']
        }
    
    # Treat any other input as a direct resolution
    result = apply_resolution(decision['id'], choice_raw, current_convo_id)
    return {
        "success": result['success'],
        "decision": decision,
        "action": "direct",
        "message": result['message']
    }


def cmd_show(args) -> int:
    """Show decision context."""
    output = show_decision_context(args.decision_id)
    print(output)
    return 0


def cmd_resolve(args) -> int:
    """Resolve a decision."""
    result = apply_resolution(
        decision_id=args.decision_id,
        resolution=args.choice,
        resolved_by_convo=args.convo or "cli",
        notes=args.notes
    )
    
    if result['success']:
        print(result['message'])
        if not result.get('route_success', True):
            print("⚠️ Warning: Routing to origin may have failed.")
        return 0
    else:
        print(f"❌ {result['message']}")
        return 1


def cmd_route(args) -> int:
    """Re-route a resolution to origin."""
    decision = find_decision_by_id(args.decision_id)
    if not decision:
        print(f"❌ Decision '{args.decision_id}' not found.")
        return 1
    
    if decision['status'] != 'resolved':
        print(f"❌ Decision not resolved yet. Status: {decision['status']}")
        return 1
    
    resolution = decision.get('resolution', 'N/A')
    notes = decision.get('resolution_notes')
    
    success = route_to_origin(decision, resolution, notes)
    
    if success:
        print(f"✅ Routed resolution to {decision['origin']}")
        return 0
    else:
        print(f"❌ Failed to route to {decision['origin']}")
        return 1


def cmd_from_sms(args) -> int:
    """Handle SMS command."""
    result = resolve_from_sms(args.message, args.convo or "sms")
    print(result['message'])
    return 0 if result['success'] else 1


def main():
    parser = argparse.ArgumentParser(
        description="Cross-Thread Resolution Handler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 N5/scripts/resolve_decision.py show d7f3a1b2
  python3 N5/scripts/resolve_decision.py resolve d7f3 --choice "A" --notes "Per discussion"
  python3 N5/scripts/resolve_decision.py route d7f3a1b2
  python3 N5/scripts/resolve_decision.py from-sms "n5 decision d7f3 approve"

SMS patterns:
  n5 decision <id>             - View decision details
  n5 decision <id> A           - Choose option A
  n5 decision <id> approve     - Quick approve
  n5 decision <id> reject      - Quick reject
  n5 decision <id> custom: X   - Custom instruction
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # show
    show_parser = subparsers.add_parser("show", help="Show decision context")
    show_parser.add_argument("decision_id", help="Decision ID (full or short)")
    
    # resolve
    resolve_parser = subparsers.add_parser("resolve", help="Resolve a decision")
    resolve_parser.add_argument("decision_id", help="Decision ID")
    resolve_parser.add_argument("--choice", required=True, help="Resolution choice")
    resolve_parser.add_argument("--notes", help="Additional notes")
    resolve_parser.add_argument("--convo", help="Resolving conversation ID")
    
    # route
    route_parser = subparsers.add_parser("route", help="Re-route resolution to origin")
    route_parser.add_argument("decision_id", help="Decision ID")
    
    # from-sms
    sms_parser = subparsers.add_parser("from-sms", help="Handle SMS command")
    sms_parser.add_argument("message", help="Full SMS message text")
    sms_parser.add_argument("--convo", help="Current conversation ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Initialize pending_decisions DB
    pending_decisions.init_db()
    
    if args.command == "show":
        return cmd_show(args)
    elif args.command == "resolve":
        return cmd_resolve(args)
    elif args.command == "route":
        return cmd_route(args)
    elif args.command == "from-sms":
        return cmd_from_sms(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
