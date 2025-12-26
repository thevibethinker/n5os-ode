"""Core data structures and helpers for the Tutor Protocol.

In this first pass we only define minimal message types and in-memory
representation. Serialization, validation, and networking will be added
in later phases.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional, Any, Dict, List


SessionMode = Literal["capability", "knowledge", "data"]


@dataclass
class SessionStart:
    """Represents the logical start of a tutor session.

    Networking and authentication details will be layered on later.
    """

    session_id: str
    peer_zo_id: str
    mode: SessionMode
    ttl_seconds: int
    created_at: datetime

    @property
    def expires_at(self) -> datetime:
        return self.created_at + timedelta(seconds=self.ttl_seconds)

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now(timezone.utc)
        return now >= self.expires_at


@dataclass
class SessionScope:
    """Describes what this session is about at a high level.

    For example, which capability or topic is being taught.
    """

    session_id: str
    description: str
    mode: SessionMode


# Teaching package schemas


@dataclass
class CapabilityPackage:
    """Representation of a "capability teaching" package.

    The ``manifest`` field is a structured dictionary with the
    following recommended keys (not all are required at this stage):

    - ``entrypoints``: list of logical entrypoints (CLI commands,
      HTTP routes, etc.).
    - ``dependencies``: list of textual dependency descriptors
      (libraries, services, environment expectations).
    - ``tests``: list of test case dicts with fields like
      ``name``, ``description``, ``kind`` (unit/integration/e2e),
      and optionally ``inputs``/``expected``.
    - ``non_functional``: constraints or expectations such as
      latency targets or throughput limits.
    """

    name: str
    version: str
    description: str
    manifest: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "capability",
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "manifest": self.manifest,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CapabilityPackage":
        if data.get("type") not in (None, "capability"):
            raise ValueError(f"Unexpected package type: {data.get('type')}")
        manifest = data.get("manifest", {}) or {}
        # Ensure manifest has the expected top-level keys with safe defaults.
        manifest.setdefault("entrypoints", [])
        manifest.setdefault("dependencies", [])
        manifest.setdefault("tests", [])
        manifest.setdefault("non_functional", {})
        return cls(
            name=data["name"],
            version=data.get("version", "0.1"),
            description=data.get("description", ""),
            manifest=manifest,
        )


@dataclass
class KnowledgePackage:
    """Representation of a "knowledge teaching" package.

    This captures a topic, a high-level outline, and body text, plus
    optional learning objectives and references.
    """

    topic: str
    outline: str
    body: str
    learning_objectives: List[str]
    references: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "knowledge",
            "topic": self.topic,
            "outline": self.outline,
            "body": self.body,
            "learning_objectives": list(self.learning_objectives),
            "references": list(self.references),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgePackage":
        if data.get("type") not in (None, "knowledge"):
            raise ValueError(f"Unexpected package type: {data.get('type')}")
        return cls(
            topic=data["topic"],
            outline=data.get("outline", ""),
            body=data.get("body", ""),
            learning_objectives=list(data.get("learning_objectives", []) or []),
            references=list(data.get("references", []) or []),
        )


@dataclass
class DataDropPackage:
    """Representation of a bounded data transfer package.

    The ``schema`` field should describe fields and types in a
    human-readable but structured way. ``record_count`` and
    ``sensitivity`` are advisory metadata for downstream safety checks.
    """

    name: str
    schema: Dict[str, Any]
    purpose: str
    preview_rows: int
    record_count: Optional[int]
    sensitivity: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "data",
            "name": self.name,
            "schema": self.schema,
            "purpose": self.purpose,
            "preview_rows": self.preview_rows,
            "record_count": self.record_count,
            "sensitivity": self.sensitivity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataDropPackage":
        if data.get("type") not in (None, "data"):
            raise ValueError(f"Unexpected package type: {data.get('type')}")
        return cls(
            name=data["name"],
            schema=data.get("schema", {}),
            purpose=data.get("purpose", ""),
            preview_rows=int(data.get("preview_rows", 0)),
            record_count=(
                int(data["record_count"]) if "record_count" in data and data["record_count"] is not None else None
            ),
            sensitivity=str(data.get("sensitivity", "unspecified")),
        )


# Additional helpers for JSON/YAML serialization can be layered on here
# once the basic shapes are validated by early demos.



