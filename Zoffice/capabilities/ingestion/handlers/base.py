"""
Ingestion Capability — Base Handler

Abstract base class for all inbound channel handlers.
Enforces the standard flow: generate UUID → security gate → classify → route → audit log → return.
"""

import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

from Zoffice.capabilities.ingestion.classify import classify_content


def _load_routing_config() -> dict:
    config_path = Path(__file__).resolve().parents[3] / "config" / "routing.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}


def _load_ingestion_config() -> dict:
    config_path = Path(__file__).resolve().parents[1] / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}


class InboundHandler:
    """Base class for all inbound channel handlers."""

    channel: str = "unknown"

    def receive(self, raw_input: dict) -> dict:
        """
        Process an inbound item through the standard pipeline.

        Returns:
            InboundItem dict with keys: id, timestamp, channel, raw_content,
            classification, routing_recommendation, security_result, tags, metadata
        """
        item_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Channel-specific content extraction
        content = self.extract_content(raw_input)
        tags = self.extract_tags(raw_input)

        # Security gate
        security_result = self._run_security_gate(content)

        # Classify
        classification = classify_content(content)

        # Route
        routing = self._resolve_route(classification, tags)

        # Audit log
        self._audit_log(item_id, content, classification, routing, security_result)

        # Log conversation
        self._log_conversation(routing, raw_input)

        return {
            "id": item_id,
            "timestamp": timestamp,
            "channel": self.channel,
            "raw_content": raw_input,
            "content": content,
            "classification": classification,
            "routing_recommendation": routing,
            "security_result": security_result,
            "tags": tags,
            "metadata": self.extract_metadata(raw_input),
        }

    def extract_content(self, raw_input: dict) -> str:
        """Override in subclass to extract text content from raw input."""
        return raw_input.get("body", raw_input.get("content", str(raw_input)))

    def extract_tags(self, raw_input: dict) -> list[str]:
        """Override in subclass to extract tags from raw input."""
        return []

    def extract_metadata(self, raw_input: dict) -> dict:
        """Override in subclass to extract channel-specific metadata."""
        return {}

    def _run_security_gate(self, content: str) -> dict:
        """Run content through the security inbound gate."""
        try:
            from Zoffice.capabilities.security.gates.inbound_gate import validate
            return validate(content)
        except Exception as e:
            return {"allowed": True, "flags": ["security_unavailable"], "filtered_content": content, "error": str(e)}

    def _resolve_route(self, classification: dict, tags: list[str]) -> str:
        """Determine which employee should handle this item."""
        ingestion_cfg = _load_ingestion_config()
        routing_cfg = _load_routing_config()

        # Tag-based routing first
        tag_routing = ingestion_cfg.get("tag_routing", {})
        for tag in tags:
            if tag.upper() in tag_routing:
                return tag_routing[tag.upper()]

        # Channel default from routing.yaml
        routes = routing_cfg.get("routes", {})
        channel_routes = routes.get(self.channel, {})
        if channel_routes.get("default"):
            return channel_routes["default"]

        # Global fallback
        return routing_cfg.get("fallback", "receptionist")

    def _audit_log(self, item_id: str, content: str, classification: dict,
                   routing: str, security_result: dict) -> None:
        """Log the inbound event to the audit trail."""
        try:
            from Zoffice.capabilities.security.audit.writer import log_audit
            log_audit(
                capability="ingestion",
                employee=None,
                action="inbound_receive",
                channel=self.channel,
                metadata={
                    "item_id": item_id,
                    "classification": classification,
                    "routing": routing,
                    "security_flags": security_result.get("flags", []),
                },
            )
        except Exception:
            pass

    def _log_conversation(self, routing: str, raw_input: dict) -> None:
        """Log the conversation start."""
        try:
            from Zoffice.capabilities.memory.conversation_logger import log_conversation
            log_conversation(
                channel=self.channel,
                employee=routing,
                summary=f"Inbound {self.channel} received",
            )
        except Exception:
            pass
