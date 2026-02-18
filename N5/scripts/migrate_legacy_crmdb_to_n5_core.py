#!/usr/bin/env python3
"""Migrate legacy N5/data/crm.db data into N5/data/n5_core.db."""

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from pathlib import Path

WORKSPACE = Path('/home/workspace')
LEGACY_DB = WORKSPACE / 'N5/data/crm.db'
TARGET_DB = WORKSPACE / 'N5/data/n5_core.db'


@dataclass
class Stats:
    people_inserted: int = 0
    people_matched: int = 0
    orgs_inserted: int = 0
    orgs_matched: int = 0
    interactions_inserted: int = 0
    relationships_inserted: int = 0


def normalize(s: str | None) -> str | None:
    if s is None:
        return None
    s = s.strip()
    return s or None


def find_or_create_person(cur: sqlite3.Cursor, full_name: str, email: str | None, row: sqlite3.Row, stats: Stats, dry_run: bool) -> int:
    email_norm = normalize(email)
    full_name_norm = normalize(full_name) or 'Unknown'

    person_id = None
    if email_norm:
        cur.execute("SELECT id FROM people WHERE lower(email)=lower(?) LIMIT 1", (email_norm,))
        hit = cur.fetchone()
        if hit:
            stats.people_matched += 1
            return int(hit[0])

    cur.execute("SELECT id FROM people WHERE lower(full_name)=lower(?) LIMIT 1", (full_name_norm,))
    hit = cur.fetchone()
    if hit:
        stats.people_matched += 1
        return int(hit[0])

    if dry_run:
        stats.people_inserted += 1
        return -1

    cur.execute(
        """
        INSERT INTO people (
          full_name, email, linkedin_url, company, title, category, status, priority,
          tags, first_contact_date, last_contact_date, markdown_path, source_db, source_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'legacy_crm_db', ?)
        """,
        (
            full_name_norm,
            email_norm,
            normalize(row['linkedin_url']),
            normalize(row['company']),
            normalize(row['title']),
            normalize(row['category']),
            normalize(row['status']) or 'active',
            normalize(row['priority']) or 'medium',
            normalize(row['tags']),
            normalize(row['first_contact_date']),
            normalize(row['last_contact_date']),
            normalize(row['markdown_path']),
            str(row['id']),
        ),
    )
    stats.people_inserted += 1
    return int(cur.lastrowid)


def find_or_create_org(cur: sqlite3.Cursor, org: sqlite3.Row, stats: Stats, dry_run: bool) -> int:
    name = normalize(org['name'])
    if not name:
        return -1
    cur.execute("SELECT id FROM organizations WHERE lower(name)=lower(?) LIMIT 1", (name,))
    hit = cur.fetchone()
    if hit:
        stats.orgs_matched += 1
        return int(hit[0])

    if dry_run:
        stats.orgs_inserted += 1
        return -1

    cur.execute(
        """
        INSERT INTO organizations (name, domain, industry, description, source_db, source_id)
        VALUES (?, ?, ?, ?, 'legacy_crm_db', ?)
        """,
        (
            name,
            normalize(org['domain']),
            normalize(org['industry']),
            normalize(org['notes']),
            str(org['id']),
        ),
    )
    stats.orgs_inserted += 1
    return int(cur.lastrowid)


def migrate(dry_run: bool) -> Stats:
    if not LEGACY_DB.exists():
        raise SystemExit(f'Legacy DB not found: {LEGACY_DB}')
    if not TARGET_DB.exists():
        raise SystemExit(f'Target DB not found: {TARGET_DB}')

    stats = Stats()

    with sqlite3.connect(TARGET_DB) as target_conn:
        target_conn.row_factory = sqlite3.Row
        tcur = target_conn.cursor()
        tcur.execute(f"ATTACH DATABASE '{LEGACY_DB}' AS legacy")

        # People
        tcur.execute("SELECT * FROM legacy.individuals")
        people = tcur.fetchall()
        legacy_to_target: dict[int, int] = {}
        for row in people:
            person_id = find_or_create_person(tcur, row['full_name'], row['email'], row, stats, dry_run)
            if person_id > 0:
                legacy_to_target[int(row['id'])] = person_id

        # Organizations
        tcur.execute("SELECT * FROM legacy.organizations")
        orgs = tcur.fetchall()
        for org in orgs:
            find_or_create_org(tcur, org, stats, dry_run)

        # Interactions
        tcur.execute("SELECT * FROM legacy.interactions")
        interactions = tcur.fetchall()
        for ix in interactions:
            mapped_person = legacy_to_target.get(int(ix['individual_id']))
            if not mapped_person:
                continue
            source_ref = normalize(ix['meeting_path']) or f"legacy_interaction:{ix['id']}"
            tcur.execute("SELECT id FROM interactions WHERE source_ref = ? LIMIT 1", (source_ref,))
            if tcur.fetchone() is not None:
                continue
            if dry_run:
                stats.interactions_inserted += 1
                continue
            tcur.execute(
                """
                INSERT INTO interactions (person_id, type, summary, source_ref, occurred_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    mapped_person,
                    normalize(ix['interaction_type']) or 'meeting',
                    normalize(ix['context']),
                    source_ref,
                    normalize(ix['interaction_date']) or normalize(ix['created_at']) or '1970-01-01T00:00:00',
                ),
            )
            stats.interactions_inserted += 1

        # Relationships
        tcur.execute("SELECT * FROM legacy.relationships")
        relationships = tcur.fetchall()
        for rel in relationships:
            pa = legacy_to_target.get(int(rel['person_a_id']))
            pb = legacy_to_target.get(int(rel['person_b_id']))
            if not pa or not pb:
                continue
            relationship_type = normalize(rel['relationship_type'])
            tcur.execute(
                """
                SELECT id FROM relationships
                WHERE person_a_id = ? AND person_b_id = ? AND COALESCE(relationship_type,'') = COALESCE(?, '')
                LIMIT 1
                """,
                (pa, pb, relationship_type),
            )
            if tcur.fetchone() is not None:
                continue
            if dry_run:
                stats.relationships_inserted += 1
                continue
            tcur.execute(
                """
                INSERT INTO relationships (person_a_id, person_b_id, relationship_type, notes, discovered_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    pa,
                    pb,
                    relationship_type,
                    normalize(rel['context']),
                    normalize(rel['discovered_date']) or normalize(rel['created_at']),
                ),
            )
            stats.relationships_inserted += 1

        if dry_run:
            target_conn.rollback()
        else:
            target_conn.commit()

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description='Migrate N5/data/crm.db into n5_core.db')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    stats = migrate(dry_run=args.dry_run)
    mode = 'DRY RUN' if args.dry_run else 'APPLY'
    print(f'Migration mode: {mode}')
    print(f'people_inserted={stats.people_inserted}')
    print(f'people_matched={stats.people_matched}')
    print(f'orgs_inserted={stats.orgs_inserted}')
    print(f'orgs_matched={stats.orgs_matched}')
    print(f'interactions_inserted={stats.interactions_inserted}')
    print(f'relationships_inserted={stats.relationships_inserted}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
