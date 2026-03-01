"""
Publishing — Content Pipeline

State machine for content lifecycle: draft → review → approved → published.
Enforces mandatory review gate. In-memory state tracking for Layer 1.
"""

import uuid
from datetime import datetime, timezone


# Valid transitions: {state: {event: next_state}}
TRANSITIONS = {
    "draft": {"submit_for_review": "review"},
    "review": {"approve": "approved", "reject": "draft"},
    "approved": {"publish": "published", "reject": "draft"},
    "published": {"archive": "archived"},
    "archived": {},
}


class ContentPipeline:
    """Content lifecycle state machine."""

    def __init__(self):
        self._items: dict[str, dict] = {}

    def create_item(
        self,
        content: str,
        slug: str,
        author: str | None = None,
    ) -> str:
        """
        Create a new content item in draft state.

        Returns:
            Item ID (UUID string).
        """
        item_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        self._items[item_id] = {
            "id": item_id,
            "content": content,
            "slug": slug,
            "author": author,
            "state": "draft",
            "created_at": now,
            "updated_at": now,
            "history": [{"state": "draft", "event": "created", "timestamp": now}],
        }

        self._audit("content_created", {"item_id": item_id, "slug": slug})
        return item_id

    def advance(self, item_id: str, event: str) -> str:
        """
        Advance a content item via an event.

        Returns:
            New state string.

        Raises:
            ValueError: If the item doesn't exist or transition is invalid.
        """
        if item_id not in self._items:
            raise ValueError(f"Unknown item: {item_id}")

        item = self._items[item_id]
        current = item["state"]

        if current not in TRANSITIONS:
            raise ValueError(f"Item in terminal state: {current}")

        valid = TRANSITIONS[current]
        if event not in valid:
            raise ValueError(
                f"Invalid event '{event}' for state '{current}'. "
                f"Valid events: {list(valid.keys())}"
            )

        new_state = valid[event]
        now = datetime.now(timezone.utc).isoformat()
        item["state"] = new_state
        item["updated_at"] = now
        item["history"].append({"state": new_state, "event": event, "timestamp": now})

        self._audit("content_state_change", {
            "item_id": item_id,
            "from": current,
            "to": new_state,
            "event": event,
        })

        return new_state

    def get_item(self, item_id: str) -> dict:
        """Get an item by ID."""
        if item_id not in self._items:
            raise ValueError(f"Unknown item: {item_id}")
        return dict(self._items[item_id])

    def list_items(self, state: str | None = None) -> list[dict]:
        """List items, optionally filtered by state."""
        items = list(self._items.values())
        if state:
            items = [i for i in items if i["state"] == state]
        return [dict(i) for i in items]

    def _audit(self, action: str, metadata: dict) -> None:
        try:
            from Zoffice.capabilities.security.audit.writer import log_audit
            log_audit(capability="publishing", employee=None, action=action, metadata=metadata)
        except Exception:
            pass
