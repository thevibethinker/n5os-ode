"""
Ingestion — Voice Handler

Skeleton for voice/VAPI webhook intake.
Always routes to receptionist in Layer 1. Extended by VAPI integration in Layer 2.
"""

from Zoffice.capabilities.ingestion.handlers.base import InboundHandler


class VoiceHandler(InboundHandler):
    channel = "voice"

    def extract_content(self, raw_input: dict) -> str:
        return raw_input.get("transcript", raw_input.get("content", ""))

    def extract_metadata(self, raw_input: dict) -> dict:
        return {
            "caller_phone": raw_input.get("caller_phone", ""),
            "caller_name": raw_input.get("caller_name", ""),
        }
