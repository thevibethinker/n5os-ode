"""
Memory Capability — Contact Manager

CRUD operations for the contacts table. Upsert logic: if email OR phone
matches an existing contact, update that record. Otherwise create new.
"""

import uuid
from datetime import datetime, timezone

from Zoffice.capabilities.memory.db_helpers import get_db


def upsert_contact(
    name: str,
    email: str | None = None,
    phone: str | None = None,
    organization: str | None = None,
    relationship: str | None = None,
    tags: list[str] | None = None,
    profile: dict | None = None,
    db_path: str | None = None,
) -> str:
    """
    Create or update a contact. Matches on email or phone for upsert.

    Returns:
        Contact ID (UUID string).
    """
    import json

    conn = get_db(db_path)
    now = datetime.now(timezone.utc)

    # Check for existing contact by email or phone
    existing = None
    if email:
        rows = conn.execute("SELECT id FROM contacts WHERE email = ?", [email]).fetchall()
        if rows:
            existing = rows[0][0]
    if existing is None and phone:
        rows = conn.execute("SELECT id FROM contacts WHERE phone = ?", [phone]).fetchall()
        if rows:
            existing = rows[0][0]

    if existing:
        # Update existing contact
        updates = []
        params = []
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if phone is not None:
            updates.append("phone = ?")
            params.append(phone)
        if organization is not None:
            updates.append("organization = ?")
            params.append(organization)
        if relationship is not None:
            updates.append("relationship = ?")
            params.append(relationship)
        if tags is not None:
            updates.append("tags = ?")
            params.append(tags)
        if profile is not None:
            updates.append("profile = ?")
            params.append(json.dumps(profile, default=str))
        updates.append("last_contact = ?")
        params.append(now)
        updates.append("interaction_count = interaction_count + 1")
        params.append(existing)

        conn.execute(
            f"UPDATE contacts SET {', '.join(updates)} WHERE id = ?",
            params,
        )
        return existing
    else:
        # Create new contact
        contact_id = str(uuid.uuid4())
        profile_json = json.dumps(profile, default=str) if profile else None
        conn.execute(
            """
            INSERT INTO contacts (id, name, email, phone, organization, relationship,
                                  first_contact, last_contact, interaction_count, profile, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [contact_id, name, email, phone, organization, relationship,
             now, now, 1, profile_json, tags],
        )
        return contact_id


def find_contact(
    email: str | None = None,
    phone: str | None = None,
    name: str | None = None,
    db_path: str | None = None,
) -> dict | None:
    """
    Look up a contact by email, phone, or name.

    Returns:
        Contact dict or None if not found.
    """
    conn = get_db(db_path)
    conditions = []
    params = []
    if email:
        conditions.append("email = ?")
        params.append(email)
    if phone:
        conditions.append("phone = ?")
        params.append(phone)
    if name:
        conditions.append("name = ?")
        params.append(name)

    if not conditions:
        return None

    where = " OR ".join(conditions)
    result = conn.execute(
        f"SELECT * FROM contacts WHERE {where} LIMIT 1", params
    )
    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()
    if not rows:
        return None
    return dict(zip(columns, rows[0]))


def get_contact(id: str, db_path: str | None = None) -> dict | None:
    """Direct lookup by contact ID."""
    conn = get_db(db_path)
    result = conn.execute("SELECT * FROM contacts WHERE id = ?", [id])
    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()
    if not rows:
        return None
    return dict(zip(columns, rows[0]))


def update_contact(id: str, db_path: str | None = None, **fields) -> bool:
    """
    Partial update of a contact.

    Returns:
        True if the contact was found and updated.
    """
    import json

    if not fields:
        return False
    conn = get_db(db_path)
    updates = []
    params = []
    for key, val in fields.items():
        if key in ("name", "email", "phone", "organization", "relationship"):
            updates.append(f"{key} = ?")
            params.append(val)
        elif key == "tags":
            updates.append("tags = ?")
            params.append(val)
        elif key == "profile":
            updates.append("profile = ?")
            params.append(json.dumps(val, default=str))

    if not updates:
        return False
    params.append(id)
    conn.execute(f"UPDATE contacts SET {', '.join(updates)} WHERE id = ?", params)
    # Check if row existed
    rows = conn.execute("SELECT id FROM contacts WHERE id = ?", [id]).fetchall()
    return len(rows) > 0


def list_contacts(
    relationship: str | None = None,
    tag: str | None = None,
    limit: int = 50,
    db_path: str | None = None,
) -> list[dict]:
    """List contacts with optional filters."""
    conn = get_db(db_path)
    conditions = []
    params = []
    if relationship:
        conditions.append("relationship = ?")
        params.append(relationship)
    if tag:
        conditions.append("list_contains(tags, ?)")
        params.append(tag)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    params.append(limit)
    result = conn.execute(
        f"SELECT * FROM contacts {where} ORDER BY last_contact DESC LIMIT ?",
        params,
    )
    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()
    return [dict(zip(columns, row)) for row in rows]
