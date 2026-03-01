"""
Ingestion — Webhook Handler

Generic webhook receiver. Routes based on source→employee mappings in config.yaml.
"""

from pathlib import Path

import yaml

from Zoffice.capabilities.ingestion.handlers.base import InboundHandler


class WebhookHandler(InboundHandler):
    channel = "webhook"

    def extract_content(self, raw_input: dict) -> str:
        payload = raw_input.get("payload", {})
        if isinstance(payload, dict):
            return str(payload.get("body", payload.get("message", str(payload))))
        return str(payload)

    def extract_tags(self, raw_input: dict) -> list[str]:
        source = raw_input.get("source", "")
        return [source] if source else []

    def extract_metadata(self, raw_input: dict) -> dict:
        return {
            "source": raw_input.get("source", ""),
            "signature": raw_input.get("signature", None),
        }

    def _resolve_route(self, classification: dict, tags: list[str]) -> str:
        """Source-based routing from ingestion config."""
        config_path = Path(__file__).resolve().parents[1] / "config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                cfg = yaml.safe_load(f)
            source_routing = cfg.get("source_routing", {})
            for tag in tags:
                if tag.lower() in source_routing:
                    return source_routing[tag.lower()]
        return super()._resolve_route(classification, tags)
