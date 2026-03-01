"""
Ingestion — Zo2Zo Handler

Handles inbound messages from other Zo instances.
Checks trust registry from security.yaml. Untrusted sources are flagged but still processed.
"""

from pathlib import Path

import yaml

from Zoffice.capabilities.ingestion.handlers.base import InboundHandler


class Zo2ZoHandler(InboundHandler):
    channel = "zo2zo"

    def extract_content(self, raw_input: dict) -> str:
        return raw_input.get("content", "")

    def extract_metadata(self, raw_input: dict) -> dict:
        return {
            "source_instance": raw_input.get("source_instance", ""),
            "has_api_key": bool(raw_input.get("api_key")),
        }

    def receive(self, raw_input: dict) -> dict:
        """Override to add trust checking before standard pipeline."""
        item = super().receive(raw_input)

        # Trust check
        source_instance = raw_input.get("source_instance", "")
        trusted = self._check_trust(source_instance)

        if not trusted:
            item["security_result"] = {
                **item.get("security_result", {}),
                "trust_status": "untrusted",
                "source_instance": source_instance,
            }
        else:
            item["security_result"] = {
                **item.get("security_result", {}),
                "trust_status": "trusted",
                "source_instance": source_instance,
            }

        return item

    def _check_trust(self, source_instance: str) -> bool:
        """Check if the source instance is in the trusted list."""
        security_config_path = Path(__file__).resolve().parents[3] / "config" / "security.yaml"
        if security_config_path.exists():
            with open(security_config_path) as f:
                cfg = yaml.safe_load(f)
            trusted_instances = cfg.get("security", {}).get("trust", {}).get("trusted_instances", [])
            return source_instance in trusted_instances
        return False
