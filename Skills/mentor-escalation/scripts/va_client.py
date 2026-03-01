#!/usr/bin/env python3
"""
VA Client - zoputer-side API client for mentor escalation communication

Communicates with va.zo.computer via /zo/ask API for guidance and oversight.
All calls are logged to the dual-sided audit system.

Usage:
    python3 va_client.py ping
    python3 va_client.py ask "How should I handle this situation?"
    python3 va_client.py escalate --question "Should I modify this workflow?" --context '{"client": "X"}'

Requires:
    VA_API_KEY environment variable (va's API key for zoputer to call)
"""

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import importlib.util

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import requests
except ImportError:
    print("Error: requests library required. Run: pip install requests")
    sys.exit(1)

# Configuration
VA_API_URL = "https://api.zo.computer/zo/ask"
TIMEOUT_SECONDS = 60  # Longer timeout for complex questions
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # seconds

# Audit logger path
AUDIT_LOGGER = Path("/home/workspace/Skills/audit-system/scripts/audit_logger.py")
SANITIZER_PATH = Path("/home/workspace/Integrations/zoputer-sync/sanitizer.py")


def get_api_key() -> str:
    """Get the va API key from environment."""
    key = os.environ.get("VA_API_KEY")
    if not key:
        print("Error: VA_API_KEY environment variable not set")
        print("Add it in Zo Settings > Developers > Secrets")
        print("See Documents/consulting/va-api-setup-guide.md for setup instructions")
        sys.exit(1)
    return key


def log_audit(entry_type: str, direction: str, payload: dict, correlation_id: Optional[str] = None) -> None:
    """Log to the audit system if available."""
    if not AUDIT_LOGGER.exists():
        return
    
    import subprocess
    try:
        cmd = [
            "python3", str(AUDIT_LOGGER),
            "log",
            "--type", entry_type,
            "--direction", direction,
            "--payload", json.dumps(payload),
        ]
        if correlation_id:
            cmd.extend(["--correlation-id", correlation_id])
        
        subprocess.run(cmd, capture_output=True, timeout=5)
    except Exception:
        pass  # Don't fail operations if audit logging fails


def _load_sanitizer() -> Optional[Any]:
    """Load the sanitizer module if available."""
    if not SANITIZER_PATH.exists():
        return None
    
    spec = importlib.util.spec_from_file_location("sanitizer", SANITIZER_PATH)
    if spec is None:
        return None
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VA_SANITIZER = _load_sanitizer()


def _sanitize_prompt(prompt: str) -> tuple[str, str, str]:
    """Sanitize the prompt using the VA_SANITIZER if available."""
    if not VA_SANITIZER:
        return prompt, "sanitizer-missing", ""
    result = VA_SANITIZER.sanitize_for_tool_call(prompt, tool_name="va-api")
    sanitized = result.sanitized_text
    canary = VA_SANITIZER.embed_canary()
    final_prompt = VA_SANITIZER.build_guarded_prompt(sanitized, canary)
    summary = VA_SANITIZER.summarize_sanitization(result)
    return final_prompt, summary, canary


def call_va(prompt: str, correlation_id: Optional[str] = None) -> dict:
    """
    Call va via /zo/ask API with retry logic.
    
    Args:
        prompt: The prompt to send to va
        correlation_id: Optional correlation ID for audit linking
    
    Returns:
        Response dict with 'output' key
    
    Raises:
        Exception on failure after retries
    """
    api_key = get_api_key()
    
    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }
    
    sanitized_prompt, sanitization_summary, canary = _sanitize_prompt(prompt)
    
    payload = {
        "input": sanitized_prompt
    }
    
    # Log outbound request
    log_audit(
        entry_type="mentor_escalation",
        direction="zoputer-to-va",
        payload={"prompt_preview": sanitized_prompt[:200], "correlation_id": correlation_id, "sanitization_summary": sanitization_summary, "canary": canary},
        correlation_id=correlation_id
    )
    
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                VA_API_URL,
                headers=headers,
                json=payload,
                timeout=TIMEOUT_SECONDS
            )
            
            if response.status_code == 200:
                result = response.json()
                output = result.get("output", "")
                if VA_SANITIZER and canary:
                    try:
                        VA_SANITIZER.guard_output(output, canary, strict=True)
                    except Exception as exc:
                        log_audit(
                            entry_type="sanitizer_block",
                            direction="va-to-zoputer",
                            payload={"error": str(exc), "correlation_id": correlation_id, "canary": canary},
                            correlation_id=correlation_id,
                        )
                        raise
                
                # Log successful response
                log_audit(
                    entry_type="mentor_response",
                    direction="va-to-zoputer",
                    payload={"status": "success", "correlation_id": correlation_id, "sanitization_summary": sanitization_summary, "canary": canary},
                    correlation_id=correlation_id
                )
                
                return result
            
            elif response.status_code == 401:
                print("Error: Authentication failed. Check VA_API_KEY.")
                log_audit(
                    entry_type="api_error",
                    direction="va-to-zoputer",
                    payload={"error": "auth_failed", "status_code": 401},
                    correlation_id=correlation_id
                )
                sys.exit(1)
            
            else:
                last_error = f"HTTP {response.status_code}: {response.text}"
        
        except requests.Timeout:
            last_error = "Request timed out"
        except requests.ConnectionError as e:
            last_error = f"Connection error: {e}"
        except Exception as e:
            last_error = f"Unexpected error: {e}"
        
        # Retry with exponential backoff
        if attempt < MAX_RETRIES - 1:
            wait_time = RETRY_BACKOFF_BASE ** attempt
            print(f"Attempt {attempt + 1} failed: {last_error}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
    
    # All retries exhausted
    log_audit(
        entry_type="api_error",
        direction="zoputer-to-va",
        payload={"error": last_error, "retries_exhausted": True},
        correlation_id=correlation_id
    )
    
    raise Exception(f"Failed after {MAX_RETRIES} attempts: {last_error}")


def cmd_ping(args) -> int:
    """Ping va to check connectivity."""
    correlation_id = f"ping-{uuid.uuid4().hex[:8]}"
    
    print("Pinging va.zo.computer...")
    start_time = time.time()
    
    try:
        # Simple ping prompt
        prompt = """You are va, the Master Zo. Respond with a JSON object:
{
  "status": "online",
  "instance": "va", 
  "timestamp": "<current UTC ISO timestamp>",
  "message": "Master Zo ready for guidance"
}
Respond ONLY with the JSON, no other text."""

        result = call_va(prompt, correlation_id)
        elapsed = time.time() - start_time
        
        output = result.get("output", "")
        
        print(f"\n✓ va responded in {elapsed:.2f}s")
        print(f"Connection: healthy")
        print(f"Bridge: bidirectional")
        
        return 0
    
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n✗ Ping failed after {elapsed:.2f}s")
        print(f"Error: {e}")
        return 1


def cmd_ask(args) -> int:
    """Send a question to va for guidance."""
    correlation_id = f"ask-{uuid.uuid4().hex[:8]}"
    
    print("Asking va for guidance...")
    
    try:
        # Format the prompt as a mentor-apprentice question
        prompt = f"""You are va, the Master Zo, providing guidance to zoputer (your apprentice).

QUESTION FROM ZOPUTER:
{args.question}

Provide strategic guidance as a mentor would to an apprentice. Include:
1. Your recommendation
2. Reasoning behind the recommendation
3. Any important considerations or risks
4. Whether this sets a precedent for similar future decisions

Respond in a clear, direct manner that helps zoputer learn the underlying principles."""

        result = call_va(prompt, correlation_id)
        output = result.get("output", "")
        
        print("\n" + "="*60)
        print("VA GUIDANCE:")
        print("="*60)
        print(output)
        print("="*60)
        
        return 0
    
    except Exception as e:
        print(f"\n✗ Ask failed: {e}")
        return 1


def cmd_escalate(args) -> int:
    """Send a structured escalation to va."""
    correlation_id = f"escalate-{uuid.uuid4().hex[:8]}"
    
    print("Escalating to va...")
    
    try:
        # Parse context if provided
        context = {}
        if args.context:
            try:
                context = json.loads(args.context)
            except json.JSONDecodeError:
                print("Warning: Invalid JSON in context, treating as plain text")
                context = {"raw_context": args.context}
        
        # Create structured escalation request
        escalation = {
            "type": "mentor_escalation",
            "from": "zoputer",
            "confidence": args.confidence,
            "situation": args.question,
            "context": context,
            "question": args.question,
            "correlation_id": correlation_id
        }
        
        # Format as a structured prompt
        prompt = f"""You are va, the Master Zo. Zoputer is escalating a decision that requires your guidance.

ESCALATION REQUEST:
```json
{json.dumps(escalation, indent=2)}
```

Provide a mentor response that includes:
1. Your recommendation (specific guidance)
2. Rationale (why this is the best approach) 
3. Whether this sets a precedent for similar future decisions
4. Any learning points for zoputer to remember

Be direct and actionable. This is mentor-to-apprentice guidance that should help zoputer learn decision-making principles."""

        result = call_va(prompt, correlation_id)
        output = result.get("output", "")
        
        print("\n" + "="*60)
        print("VA ESCALATION RESPONSE:")
        print("="*60)
        print(output)
        print("="*60)
        
        return 0
    
    except Exception as e:
        print(f"\n✗ Escalation failed: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="VA Client - escalate decisions to va for guidance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 va_client.py ping
  python3 va_client.py ask "Should I modify workflow X for client Y?"
  python3 va_client.py escalate \\
    --question "Client wants to remove review gate" \\
    --confidence 0.6 \\
    --context '{"client": "startup_a", "workflow": "hiring"}'
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # ping
    subparsers.add_parser("ping", help="Check connectivity to va")
    
    # ask
    ask_parser = subparsers.add_parser("ask", help="Ask va a question")
    ask_parser.add_argument("question", help="Question for va")
    
    # escalate
    escalate_parser = subparsers.add_parser("escalate", help="Send structured escalation to va")
    escalate_parser.add_argument("--question", required=True, help="Question/situation to escalate")
    escalate_parser.add_argument("--confidence", type=float, default=0.5, help="Confidence level 0.0-1.0")
    escalate_parser.add_argument("--context", help="JSON context object")
    
    args = parser.parse_args()
    
    if args.command == "ping":
        sys.exit(cmd_ping(args))
    elif args.command == "ask":
        sys.exit(cmd_ask(args))
    elif args.command == "escalate":
        sys.exit(cmd_escalate(args))
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()