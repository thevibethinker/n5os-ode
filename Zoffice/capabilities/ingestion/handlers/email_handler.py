"""
Ingestion — Email Handler

Parses email input, extracts [TAG] patterns from subject lines,
and routes based on tag mappings in config.yaml.
"""

import re

from Zoffice.capabilities.ingestion.handlers.base import InboundHandler


class EmailHandler(InboundHandler):
    channel = "email"

    def extract_content(self, raw_input: dict) -> str:
        subject = raw_input.get("subject", "")
        body = raw_input.get("body", "")
        return f"{subject} {body}".strip()

    def extract_tags(self, raw_input: dict) -> list[str]:
        """Extract [TAG] patterns from subject line."""
        subject = raw_input.get("subject", "")
        return re.findall(r'\[([A-Z0-9_]+)\]', subject.upper())

    def extract_metadata(self, raw_input: dict) -> dict:
        return {
            "from": raw_input.get("from", ""),
            "subject": raw_input.get("subject", ""),
            "tags": self.extract_tags(raw_input),
        }
