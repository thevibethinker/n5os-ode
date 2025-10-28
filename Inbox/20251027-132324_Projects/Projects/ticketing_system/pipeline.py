"""Core ticket-generation pipeline (Phases 1 → 4)."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta
import logging
from pathlib import Path

from jsonschema import validate, ValidationError

# Optional OpenAI import
try:
    from openai import OpenAI  # type: ignore
except ImportError:  # keep working without the lib
    OpenAI = None  # type: ignore

from prompts import determine_ticket_type, get_prompt

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")

ROOT = Path("/home/workspace")
SCHEMA_PATH = ROOT / "ticketing_system" / "schema.json"
KNOWLEDGE_PATH = ROOT / "knowledge_base.json"
TICKETS_STORE = ROOT / "ticketing_system" / "tickets_store.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return default

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ---------------------------------------------------------------------------
# Knowledge base & ticket store
# ---------------------------------------------------------------------------

def load_knowledge_base() -> dict:
    return load_json(KNOWLEDGE_PATH, {})

def load_ticket_store() -> list[dict]:
    return load_json(TICKETS_STORE, [])

def save_ticket_store(tickets: list[dict]):
    save_json(TICKETS_STORE, tickets)

# ---------------------------------------------------------------------------
# LLM extraction (optional)
# ---------------------------------------------------------------------------

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if (api_key and OpenAI) else None  # type: ignore


def _llm_extract(meeting_data: dict, context: str, knowledge_base: dict) -> dict:
    """Call OpenAI (if available) to extract structured info."""
    if client is None:
        logging.warning("LLM unavailable – using fallback extraction.")
        return {
            "actionable_items": [],
            "blurbs": [],
            "warm_intro_cues": [],
            "priority": "medium",
            "output_type": "report",
        }

    ticket_type = determine_ticket_type(meeting_data)
    meeting_text = (
        f"Content: {meeting_data.get('content_map','')}\n"
        f"Core: {meeting_data.get('core_map','')}\n"
        f"Operations: {meeting_data.get('operations_map','')}"
    )
    kb_text = json.dumps(knowledge_base, indent=2)[:4000]  # keep prompt reasonable

    prompt = (
        "Use the following knowledge base to enrich the ticket for Careerspan:\n" + kb_text + "\n\n" +
        get_prompt(ticket_type, meeting_text, context) +
        "\nRespond in JSON with keys actionable_items, blurbs, warm_intro_cues, priority, output_type."
    )

    try:
        rsp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.4,
        )
        return json.loads(rsp.choices[0].message.content.strip())  # type: ignore
    except Exception as e:  # pragma: no cover
        logging.error("LLM extraction failed: %s", e)
        return {
            "actionable_items": [],
            "blurbs": [],
            "warm_intro_cues": [],
            "priority": "medium",
            "output_type": "report",
        }

# ---------------------------------------------------------------------------
# Ticket helpers
# ---------------------------------------------------------------------------

def _determine_categories(text: str) -> list[str]:
    text = text.lower()
    cats: list[str] = []
    if any(k in text for k in ["community", "partner", "collaboration"]):
        cats.append("community partner")
    if any(k in text for k in ["hiring", "recruit", "customer", "client"]):
        cats.append("hiring partner (a customer)")
    if any(k in text for k in ["networking", "relationship", "connection"]):
        cats.append("networking relationship")
    if any(k in text for k in ["lead", "opportunity", "prospect", "miscellaneous"]):
        cats.append("general lead or miscellaneous lead")
    if not cats:
        cats.append("general lead or miscellaneous lead")
    return cats


def _context_summary(title: str, participants: list[str], categories: list[str], priority: str) -> str:
    return (
        f"This ticket covers {title}. Participants: {', '.join(participants)}. "
        f"Key focus areas: {', '.join(categories)}. Priority: {priority}."
    )


def _content_hints(categories: list[str], output_type: str, items: list[str]) -> list[str]:
    hints: list[str] = []
    if "community partner" in categories:
        hints += [
            "Develop community engagement content or partnership proposals",
            "Create collaborative project outlines or shared initiatives",
        ]
    if "hiring partner (a customer)" in categories:
        hints += [
            "Prepare hiring strategy documents or candidate profiles",
            "Draft customer-focused communications or service agreements",
        ]
    if "networking relationship" in categories:
        hints += [
            "Build networking event summaries or relationship maps",
            "Generate follow-up communications for relationship building",
        ]
    if "general lead or miscellaneous lead" in categories:
        hints += [
            "Create lead nurturing content or opportunity assessments",
            "Develop miscellaneous reports or general follow-ups",
        ]
    hints.append(f"Generate a {output_type} summarizing the meeting outcomes and next steps")
    return hints


def _find_related(ticket: dict, store: list[dict]) -> list[str]:
    rel: set[str] = set()
    parts = set(ticket.get("meeting_metadata", {}).get("participants", []))
    title_words = set(ticket["title"].lower().split())
    for t in store:
        if parts & set(t.get("meeting_metadata", {}).get("participants", [])):
            rel.add(t["id"])
        elif title_words & set(t["title"].lower().split()):
            rel.add(t["id"])
    return list(rel)


def _assign(ticket: dict) -> str:
    # simplistic assignment demo
    participants = ticket.get("meeting_metadata", {}).get("participants", [])
    for p in ("John", "Sarah", "Mike"):
        if p in participants:
            return p
    return participants[0] if participants else "unassigned"

# ---------------------------------------------------------------------------
# Main generation function
# ---------------------------------------------------------------------------

SCHEMA = load_json(SCHEMA_PATH, {})


def generate_ticket(meeting_data: dict) -> dict:
    kb = load_knowledge_base()
    store = load_ticket_store()

    title = meeting_data.get("core_map", "Meeting Ticket")[:80]
    ticket: dict = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": meeting_data.get("core_map", ""),
        "meeting_metadata": meeting_data.get("metadata", {}),
        "version": "1.0",
    }

    # Context enrichment
    participants = ticket["meeting_metadata"].get("participants", [])
    context = " ".join(kb.get("team_roles", {}).get(p, "") for p in participants)
    context += " " + kb.get("project_timeline", "")

    # LLM extraction / fallback
    extracted = _llm_extract(meeting_data, context, kb)
    ticket.update({k: extracted.get(k) for k in ["actionable_items", "blurbs", "warm_intro_cues"]})
    ticket["priority"] = extracted.get("priority", "medium")
    ticket["output_type"] = extracted.get("output_type", "report")

    # Categories & summaries
    all_text = " ".join([
        meeting_data.get("content_map", ""),
        meeting_data.get("core_map", ""),
        meeting_data.get("operations_map", ""),
    ])
    cats = _determine_categories(all_text)
    ticket["categories"] = cats
    ticket["context_summary"] = _context_summary(title, participants, cats, ticket["priority"])
    ticket["content_creation_hints"] = _content_hints(cats, ticket["output_type"], ticket.get("actionable_items", []))
    ticket["contextual_enrichment"] = context
    ticket["llm_instructions"] = f"Generate a {ticket['output_type']} based on this ticket."

    # Assignment, status, etc.
    ticket["assignee"] = _assign(ticket)
    ticket["status"] = "open"
    ticket["progress"] = 0
    ticket["quality_score"] = 5
    ticket["feedback"] = []
    due_delta = {"high": 3, "medium": 7, "low": 14}[ticket["priority"]]
    ticket["due_date"] = (datetime.utcnow() + timedelta(days=due_delta)).strftime("%Y-%m-%d")

    # Related tickets
    ticket["related_tickets"] = _find_related(ticket, store)

    # Schema validation
    try:
        validate(ticket, SCHEMA)
    except ValidationError as e:  # pragma: no cover
        logging.error("Schema validation failed: %s", e)

    # persist
    store.append(ticket)
    save_ticket_store(store)
    return ticket

if __name__ == "__main__":  # quick test
    sample = {
        "content_map": "Discussed database migration and client feedback on UI.",
        "core_map": "Project update meeting.",
        "operations_map": "Migrate DB by Friday; revise UI by Monday.",
        "metadata": {
            "participants": ["John", "Sarah", "Mike"],
            "roles": {"John": "PM", "Sarah": "Designer", "Mike": "Dev"},
            "deliverables": ["DB migration", "UI redesign"],
        },
    }
    print(json.dumps(generate_ticket(sample), indent=2))
