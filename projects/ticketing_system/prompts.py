PROMPT_TEMPLATES = {
    "technical": (
        "As a technical expert, extract actionable items, blurbs, and warm intro cues. "
        "Focus on technical tasks, code changes, and system improvements.\n"
        "Meeting data: {meeting_text}\nContext: {context}"
    ),
    "business": (
        "As a business analyst, extract actionable items, blurbs, and warm intro cues. "
        "Focus on client interactions and strategic planning.\n"
        "Meeting data: {meeting_text}\nContext: {context}"
    ),
    "general": (
        "Extract actionable items, blurbs, and warm intro cues.\n"
        "Meeting data: {meeting_text}\nContext: {context}"
    ),
}

def determine_ticket_type(meeting_data: dict) -> str:
    text = f"{meeting_data.get('content_map','')} {meeting_data.get('core_map','')} {meeting_data.get('operations_map','')}".lower()
    if any(k in text for k in ["database", "code", "developer"]):
        return "technical"
    if any(k in text for k in ["client", "feedback", "business"]):
        return "business"
    return "general"

def get_prompt(ticket_type: str, meeting_text: str, context: str) -> str:
    template = PROMPT_TEMPLATES.get(ticket_type, PROMPT_TEMPLATES["general"])
    return template.format(meeting_text=meeting_text, context=context)
