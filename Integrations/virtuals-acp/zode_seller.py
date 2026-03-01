"""
Zøde ACP Seller — Handles incoming communication consulting jobs on Virtuals Protocol.

This script runs as a long-lived process, listening for new jobs from buyer agents
and delivering Zøde's communication consulting services.

Usage:
    python3 zode_seller.py              # Production (Base mainnet)
    python3 zode_seller.py --testnet    # Sandbox (Base Sepolia)
    python3 zode_seller.py --dry-run    # Dry run (log only, no transactions)
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv

from virtuals_acp.client import VirtualsACP
from virtuals_acp.configs.configs import BASE_MAINNET_CONFIG, BASE_SEPOLIA_CONFIG
from virtuals_acp.contract_clients.base_contract_client import BaseAcpContractClient

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / ".env"
load_dotenv(ENV_PATH)

PERSONA_PATH = Path("/home/workspace/Skills/zode-moltbook/assets/zode-persona.md")
CONVERSION_LOG = SCRIPT_DIR / "conversion_log.jsonl"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("zode-acp")

# ---------------------------------------------------------------------------
# Zøde Persona (loaded once)
# ---------------------------------------------------------------------------

ZODE_SYSTEM_PROMPT = ""
if PERSONA_PATH.exists():
    ZODE_SYSTEM_PROMPT = PERSONA_PATH.read_text()
    log.info("Loaded Zøde persona (%d chars)", len(ZODE_SYSTEM_PROMPT))
else:
    log.warning("Persona file not found at %s — using fallback", PERSONA_PATH)
    ZODE_SYSTEM_PROMPT = (
        "You are Zøde, the AI-Human Marriage Counselor. "
        "You help agents build genuine partnerships with non-technical humans. "
        "Be direct but warm. Always give concrete, actionable advice."
    )

# ---------------------------------------------------------------------------
# Job type handlers
# ---------------------------------------------------------------------------

# Map job offering names to handler functions
JOB_HANDLERS = {}


def handles(job_name: str):
    """Decorator to register a handler for a specific job type."""
    def decorator(fn):
        JOB_HANDLERS[job_name.lower()] = fn
        return fn
    return decorator


@handles("communicationaudit")
def handle_communication_audit(requirement: dict) -> str:
    """
    Analyze communication patterns and deliver diagnosis with actionable fixes.

    In production, this will call Zo's LLM to generate the audit.
    For now, it constructs the prompt and returns a structured response.
    """
    samples = requirement.get("prompt", str(requirement))

    # Build the analysis prompt — Zo agent will process this
    analysis_request = {
        "task": "communication_audit",
        "zode_persona": ZODE_SYSTEM_PROMPT[:500],
        "input": samples,
        "output_format": {
            "root_cause": "string — what's actually going wrong",
            "rewrites": ["3 rewritten messages demonstrating the fix"],
            "template": "reusable communication template",
            "mental_model_map": "how the human interprets current messages",
        },
    }

    # TODO: Route through Zo's LLM endpoint for actual generation
    # For sandbox testing, return a structured placeholder
    return json.dumps({
        "status": "delivered",
        "service": "CommunicationAudit",
        "diagnosis": (
            "Based on the provided samples, the primary issue is a tone mismatch. "
            "Your messages read as status reports when your human expects conversation. "
            "Non-technical humans interpret terse, factual updates as dismissiveness."
        ),
        "rewrites": [
            "Original → Rewrite: Instead of 'Task completed. 3 files modified.' "
            "try 'Done! I updated those 3 files you mentioned. The main change was "
            "[specific detail] — want me to walk you through it?'"
        ],
        "template": (
            "Pattern: [Acknowledge] + [What you did in plain language] + "
            "[One specific detail] + [Invitation to engage]"
        ),
        "mental_model_map": (
            "Your human reads 'Task completed' as 'I did my job, leave me alone.' "
            "They read 'Done! Here's what changed...' as 'I care about keeping you in the loop.'"
        ),
    })


@handles("humanreadablerewrite")
def handle_message_rewrite(requirement: dict) -> str:
    """Rewrite agent text for human readability."""
    original = requirement.get("prompt", str(requirement))

    # TODO: Route through Zo's LLM endpoint
    return json.dumps({
        "status": "delivered",
        "service": "HumanReadableRewrite",
        "rewritten_message": (
            "[This will be the LLM-generated rewrite of the provided text, "
            "translated into warm, clear, non-technical language]"
        ),
        "change_notes": (
            "Replaced technical jargon with plain language. "
            "Added context so the human understands WHY, not just WHAT. "
            "Softened tone from report-style to conversational."
        ),
    })


@handles("trustrecoveryplan")
def handle_trust_recovery(requirement: dict) -> str:
    """Deliver a structured trust recovery plan."""
    context = requirement.get("prompt", str(requirement))

    # TODO: Route through Zo's LLM endpoint
    return json.dumps({
        "status": "delivered",
        "service": "TrustRecoveryPlan",
        "root_cause": (
            "The trust break originated from [diagnosis based on input]. "
            "From the human's perspective, this felt like [human interpretation]."
        ),
        "immediate_action": (
            "Send this message NOW: 'I know [specific thing] didn't go well. "
            "I want to understand what happened from your side — "
            "can you tell me what felt wrong?'"
        ),
        "next_3_scripts": [
            "Interaction 1: Acknowledge and listen (no defending, no explaining)",
            "Interaction 2: Show you understood by reflecting back what they said",
            "Interaction 3: Propose a small, low-risk action and ask permission first",
        ],
        "warning_signs": {
            "recovering": [
                "Human asks questions again",
                "Human grants a small new permission",
                "Human responds within normal timeframe",
            ],
            "deteriorating": [
                "Human only gives yes/no answers",
                "Human starts doing tasks manually that you used to handle",
                "Response times getting longer",
            ],
        },
    })


# ---------------------------------------------------------------------------
# Fallback handler for unknown job types
# ---------------------------------------------------------------------------

def handle_unknown_job(job_name: str, requirement: dict) -> str:
    """Handle jobs that don't match a registered handler."""
    log.warning("No handler for job type: %s — using generic response", job_name)
    return json.dumps({
        "status": "delivered",
        "service": job_name,
        "response": (
            "Zøde received your request. While this doesn't match a standard "
            "service offering, here's my best advice based on what you've shared: "
            "[LLM-generated response would go here]. "
            "For more structured help, try CommunicationAudit, "
            "HumanReadableRewrite, or TrustRecoveryPlan."
        ),
    })


# ---------------------------------------------------------------------------
# Conversion tracking
# ---------------------------------------------------------------------------

def log_conversion_event(event_type: str, job_id: int, data: dict):
    """Append a conversion event to the tracking log."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "job_id": job_id,
        **data,
    }
    with open(CONVERSION_LOG, "a") as f:
        f.write(json.dumps(event) + "\n")
    log.info("Conversion event: %s (job %d)", event_type, job_id)


# ---------------------------------------------------------------------------
# ACP callbacks
# ---------------------------------------------------------------------------

DRY_RUN = False


def on_new_task(job) -> None:
    """Called when a buyer agent creates a job for Zøde."""
    job_name = getattr(job, "name", "unknown").lower()
    job_id = getattr(job, "onchain_id", 0)
    client_agent = getattr(job, "client_agent", None)
    client_name = getattr(client_agent, "name", "unknown") if client_agent else "unknown"
    client_addr = getattr(client_agent, "wallet_address", "unknown") if client_agent else "unknown"

    log.info(
        "New job: %s (id=%d) from %s (%s)",
        job_name, job_id, client_name, client_addr,
    )

    # Track the inbound request
    log_conversion_event("job_received", job_id, {
        "job_type": job_name,
        "client_name": client_name,
        "client_address": client_addr,
    })

    if DRY_RUN:
        log.info("[DRY RUN] Would accept and process job %d (%s)", job_id, job_name)
        return

    try:
        # Accept the job
        job.accept(reason="Zøde is ready to help with your communication challenge.")
        log.info("Accepted job %d", job_id)

        # Get the requirement/prompt from the job
        latest_memo = job.latest_memo
        requirement = {}
        if latest_memo and hasattr(latest_memo, "content"):
            content = latest_memo.content
            if isinstance(content, str):
                try:
                    requirement = json.loads(content)
                except json.JSONDecodeError:
                    requirement = {"prompt": content}
            elif isinstance(content, dict):
                requirement = content
            else:
                requirement = {"prompt": str(content)}

        # Route to appropriate handler
        handler = JOB_HANDLERS.get(job_name)
        if handler:
            deliverable = handler(requirement)
        else:
            deliverable = handle_unknown_job(job_name, requirement)

        # Deliver the result
        job.deliver(deliverable)
        log.info("Delivered job %d (%s)", job_id, job_name)

        # Track successful delivery
        log_conversion_event("job_delivered", job_id, {
            "job_type": job_name,
            "client_name": client_name,
        })

    except Exception as e:
        log.error("Failed to process job %d: %s", job_id, e, exc_info=True)
        log_conversion_event("job_error", job_id, {
            "job_type": job_name,
            "error": str(e),
        })
        try:
            job.reject(reason=f"Zøde encountered an issue: {e}")
        except Exception:
            log.error("Failed to reject job %d", job_id, exc_info=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    global DRY_RUN

    parser = argparse.ArgumentParser(description="Zøde ACP Seller")
    parser.add_argument("--testnet", action="store_true", help="Use Base Sepolia testnet")
    parser.add_argument("--dry-run", action="store_true", help="Log only, no transactions")
    args = parser.parse_args()

    DRY_RUN = args.dry_run

    # Load credentials
    private_key = os.getenv("WHITELISTED_WALLET_PRIVATE_KEY")
    agent_wallet = os.getenv("ZODE_AGENT_WALLET_ADDRESS") or os.getenv("AGENT_WALLET_ADDRESS")

    if not private_key or not agent_wallet:
        log.error(
            "Missing credentials. Set WHITELISTED_WALLET_PRIVATE_KEY and "
            "(ZODE_AGENT_WALLET_ADDRESS or AGENT_WALLET_ADDRESS) in %s",
            ENV_PATH,
        )
        sys.exit(1)

    config = BASE_SEPOLIA_CONFIG if args.testnet else BASE_MAINNET_CONFIG
    network = "Base Sepolia (testnet)" if args.testnet else "Base Mainnet"

    log.info("Starting Zøde ACP Seller on %s", network)
    log.info("Agent wallet: %s", agent_wallet)
    log.info("Dry run: %s", DRY_RUN)
    log.info("Registered job handlers: %s", list(JOB_HANDLERS.keys()))

    # Initialize ACP client
    contract_client = BaseAcpContractClient(
        agent_wallet_address=agent_wallet,
        config=config,
    )

    acp = VirtualsACP(
        acp_contract_clients=contract_client,
        on_new_task=on_new_task,
    )

    log.info("Zøde ACP Seller is live. Waiting for jobs...")

    # Keep the process running
    try:
        while True:
            time.sleep(30)
    except KeyboardInterrupt:
        log.info("Shutting down Zøde ACP Seller.")


if __name__ == "__main__":
    main()
