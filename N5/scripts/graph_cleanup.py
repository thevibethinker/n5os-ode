#!/usr/bin/env python3
"""
N5 Graph Cleanup — Post-backfill entity normalization.

Fixes:
1. Merges V/Vrijen variants into canonical entity
2. Normalizes entity types to 6 canonical types
3. Filters noisy/low-quality entities
4. Deduplicates near-identical entities
"""

import sqlite3
import re
import argparse
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
LOG = logging.getLogger(__name__)

BRAIN_DB = "/home/workspace/N5/cognition/brain.db"

# Canonical entity types
CANONICAL_TYPES = {"PERSON", "CONCEPT", "ORG", "BELIEF", "TOOL", "EVENT"}

# Type normalization mapping
TYPE_MAP = {
    # -> PERSON
    "CONTACT": "PERSON",
    "ROLE": "PERSON",
    "HANDLE": "PERSON",
    
    # -> ORG
    "ORGANIZATION": "ORG",
    "COMPANY": "ORG",
    "COMMUNITY": "ORG",
    "INSTITUTION": "ORG",
    
    # -> TOOL
    "SOFTWARE": "TOOL",
    "FILE": "TOOL",
    "DOCUMENT": "TOOL",
    "FUNCTION": "TOOL",
    "SKILL": "TOOL",
    "PROGRAM": "TOOL",
    "METHOD": "TOOL",
    "PROTOCOL": "TOOL",
    "AGENT": "TOOL",
    "RESOURCE": "TOOL",
    "DIRECTORY": "TOOL",
    "REGISTRY": "TOOL",
    
    # -> CONCEPT
    "STRATEGY": "CONCEPT",
    "METRIC": "CONCEPT",
    "STATUS": "CONCEPT",
    "VERSION": "CONCEPT",
    "TITLE": "CONCEPT",
    "POSITION": "CONCEPT",
    "LOCATION": "CONCEPT",
    "DATE": "CONCEPT",
    "TAG": "CONCEPT",
    "PERSONA": "CONCEPT",
    "DOCUMENTATION": "CONCEPT",
    "REPORT": "CONCEPT",
    "B2B PRODUCT": "CONCEPT",
    "BUSINESS MODEL": "CONCEPT",
    "RELATIONSHIP_CONTEXT": "CONCEPT",
    
    # -> BELIEF
    "PRINCIPLE": "BELIEF",
    "THESIS": "BELIEF",
    
    # -> EVENT
    "MEETING": "EVENT",
}

# V variants to merge (canonical: "V (Vrijen Attawar)")
V_VARIANTS = [
    "V",
    "Vrijen",
    "Vrijen Attawar",
    "V (Vrijen)",
    "V (Vrijen Attawar)",
    "V Vrijen",
    "VrijenAttawar",
    "vrijen-attawar",
    "alex-x-vrijen",
    "Alex_x_Vrijen",
    "Alex X Vrijen",
]

# Noise patterns - entities matching these get flagged for review/deletion
NOISE_PATTERNS = [
    r"^\$[\d,]+",           # Dollar amounts
    r"^\d+[\-\s]?\d*\s*(years?|months?|days?|hours?|min)",  # Time durations
    r"^\d+%",               # Percentages
    r"^https?://",          # URLs
    r"^[a-f0-9]{8,}$",      # Hashes/IDs
    r"^con_[a-zA-Z0-9]+$",  # Conversation IDs
    r"^\d{4}-\d{2}-\d{2}",  # Dates
    r"^[\d\s\-\(\)]+$",     # Phone numbers
    r"^[^a-zA-Z]*$",        # No letters at all
]

# High-value entities to never delete (case-insensitive)
PROTECTED_ENTITIES = {
    # V variants
    "v", "vrijen", "vrijen attawar", "v (vrijen)", "v (vrijen attawar)",
    # Companies/orgs
    "careerspan", "zo", "zo computer", "n5", "nira", "linkedin", 
    "corridorx", "junto club", "group midnight", "superposition",
    "meng fund", "next play", "cornell", "yale", "mckinsey",
    "google", "openai", "anthropic", "stripe", "airtable", "notion",
    # People
    "logan", "logan currie", "ilse", "ilse funkhouser", "howie",
    "griffin", "ben", "aaron", "aaron mak hoffman", "david", "david speigel",
    "sam", "ryan", "zoe", "shivam",
    # Technical acronyms that are legitimate
    "llm", "ats", "sre", "api", "cli", "sql", "css", "html", "json",
    "yaml", "gpg", "ssh", "aws", "gcp", "ml", "ai", "ux", "ui",
}


def get_stats(conn) -> dict:
    """Get current graph stats."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM entities")
    entities = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM relationships")
    relationships = cursor.fetchone()[0]
    cursor.execute("SELECT type, COUNT(*) FROM entities GROUP BY type ORDER BY COUNT(*) DESC")
    types = cursor.fetchall()
    return {"entities": entities, "relationships": relationships, "types": types}


def normalize_types(conn, dry_run: bool = True) -> dict:
    """Normalize entity types to canonical set."""
    cursor = conn.cursor()
    
    # Get current type distribution
    cursor.execute("SELECT type, COUNT(*) FROM entities GROUP BY type")
    type_counts = dict(cursor.fetchall())
    
    changes = {}
    for old_type, new_type in TYPE_MAP.items():
        if old_type in type_counts:
            changes[old_type] = {"new_type": new_type, "count": type_counts[old_type]}
            if not dry_run:
                cursor.execute("UPDATE entities SET type = ? WHERE type = ?", (new_type, old_type))
    
    # Handle unknown types -> CONCEPT
    cursor.execute("SELECT DISTINCT type FROM entities WHERE type NOT IN ({})".format(
        ",".join("?" * len(CANONICAL_TYPES))
    ), tuple(CANONICAL_TYPES))
    unknown_types = [r[0] for r in cursor.fetchall()]
    
    for ut in unknown_types:
        if ut not in TYPE_MAP:
            count = type_counts.get(ut, 0)
            changes[ut] = {"new_type": "CONCEPT", "count": count}
            if not dry_run:
                cursor.execute("UPDATE entities SET type = 'CONCEPT' WHERE type = ?", (ut,))
    
    if not dry_run:
        conn.commit()
    
    return changes


def merge_v_variants(conn, dry_run: bool = True) -> dict:
    """Merge all V/Vrijen variants into canonical entity."""
    cursor = conn.cursor()
    
    canonical_name = "V (Vrijen Attawar)"
    canonical_type = "PERSON"
    
    # Find all V variant entities
    placeholders = ",".join("?" * len(V_VARIANTS))
    cursor.execute(f"""
        SELECT id, name, type, mention_count 
        FROM entities 
        WHERE name IN ({placeholders}) OR LOWER(name) IN ({placeholders})
    """, V_VARIANTS + [v.lower() for v in V_VARIANTS])
    
    variants = cursor.fetchall()
    
    if not variants:
        return {"merged": 0, "variants": []}
    
    # Sum up mention counts
    total_mentions = sum(v[3] or 1 for v in variants)
    variant_ids = [v[0] for v in variants]
    variant_names = [v[1] for v in variants]
    
    result = {
        "merged": len(variants),
        "variants": variant_names,
        "total_mentions": total_mentions,
        "canonical": canonical_name
    }
    
    if dry_run:
        return result
    
    # Get or create canonical entity
    cursor.execute("SELECT id FROM entities WHERE name = ?", (canonical_name,))
    canonical = cursor.fetchone()
    
    if canonical:
        canonical_id = canonical[0]
        # Update mention count
        cursor.execute(
            "UPDATE entities SET mention_count = mention_count + ? WHERE id = ?",
            (total_mentions, canonical_id)
        )
    else:
        # Create canonical entity
        import uuid
        canonical_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO entities (id, name, type, canonical_name, mention_count)
            VALUES (?, ?, ?, ?, ?)
        """, (canonical_id, canonical_name, canonical_type, "v", total_mentions))
    
    # Update relationships to point to canonical
    for vid in variant_ids:
        if vid != canonical_id:
            cursor.execute(
                "UPDATE relationships SET from_entity_id = ? WHERE from_entity_id = ?",
                (canonical_id, vid)
            )
            cursor.execute(
                "UPDATE relationships SET to_entity_id = ? WHERE to_entity_id = ?",
                (canonical_id, vid)
            )
    
    # Delete variant entities (except canonical if it existed)
    for vid in variant_ids:
        if vid != canonical_id:
            cursor.execute("DELETE FROM entities WHERE id = ?", (vid,))
    
    conn.commit()
    return result


def find_noise_entities(conn) -> list:
    """Find entities that look like noise."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type, mention_count FROM entities")
    
    noise = []
    for eid, name, etype, mentions in cursor.fetchall():
        # Skip protected entities
        if name.lower() in PROTECTED_ENTITIES:
            continue
        
        # Check noise patterns
        is_noise = False
        for pattern in NOISE_PATTERNS:
            if re.match(pattern, name, re.IGNORECASE):
                is_noise = True
                break
        
        # Single-mention entities with very short names (but allow 3-char acronyms)
        if not is_noise and (mentions or 1) == 1 and len(name) <= 2:
            is_noise = True
        
        # Entities that are just whitespace or special chars
        if not is_noise and not re.search(r'[a-zA-Z]{2,}', name):
            is_noise = True
        
        if is_noise:
            noise.append({"id": eid, "name": name, "type": etype, "mentions": mentions})
    
    return noise


def delete_noise_entities(conn, noise_ids: list, dry_run: bool = True) -> int:
    """Delete noise entities and their relationships."""
    if dry_run or not noise_ids:
        return len(noise_ids)
    
    cursor = conn.cursor()
    
    # Delete relationships first
    placeholders = ",".join("?" * len(noise_ids))
    cursor.execute(f"DELETE FROM relationships WHERE from_entity_id IN ({placeholders})", noise_ids)
    cursor.execute(f"DELETE FROM relationships WHERE to_entity_id IN ({placeholders})", noise_ids)
    
    # Delete entities
    cursor.execute(f"DELETE FROM entities WHERE id IN ({placeholders})", noise_ids)
    
    conn.commit()
    return len(noise_ids)


def deduplicate_entities(conn, dry_run: bool = True) -> dict:
    """Find and merge case-insensitive duplicates."""
    cursor = conn.cursor()
    
    # Find duplicates by lowercase name
    cursor.execute("""
        SELECT LOWER(name) as lname, COUNT(*) as cnt
        FROM entities
        GROUP BY LOWER(name)
        HAVING COUNT(*) > 1
    """)
    
    duplicates = cursor.fetchall()
    merged = 0
    
    for lname, count in duplicates:
        # Get all variants
        cursor.execute("""
            SELECT id, name, type, mention_count
            FROM entities
            WHERE LOWER(name) = ?
            ORDER BY mention_count DESC
        """, (lname,))
        
        variants = cursor.fetchall()
        if len(variants) <= 1:
            continue
        
        # Keep the one with most mentions
        keep_id, keep_name, keep_type, keep_mentions = variants[0]
        
        if not dry_run:
            # Sum mentions
            total_mentions = sum(v[3] or 1 for v in variants)
            cursor.execute(
                "UPDATE entities SET mention_count = ? WHERE id = ?",
                (total_mentions, keep_id)
            )
            
            # Update relationships
            for vid, vname, vtype, vmentions in variants[1:]:
                cursor.execute(
                    "UPDATE relationships SET from_entity_id = ? WHERE from_entity_id = ?",
                    (keep_id, vid)
                )
                cursor.execute(
                    "UPDATE relationships SET to_entity_id = ? WHERE to_entity_id = ?",
                    (keep_id, vid)
                )
                cursor.execute("DELETE FROM entities WHERE id = ?", (vid,))
        
        merged += len(variants) - 1
    
    if not dry_run:
        conn.commit()
    
    return {"duplicates_found": len(duplicates), "entities_merged": merged}


def main():
    parser = argparse.ArgumentParser(description="N5 Graph Cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--types", action="store_true", help="Normalize entity types")
    parser.add_argument("--merge-v", action="store_true", help="Merge V/Vrijen variants")
    parser.add_argument("--noise", action="store_true", help="Find/remove noise entities")
    parser.add_argument("--dedupe", action="store_true", help="Deduplicate entities")
    parser.add_argument("--all", action="store_true", help="Run all cleanup steps")
    parser.add_argument("--stats", action="store_true", help="Show current stats")
    args = parser.parse_args()
    
    conn = sqlite3.connect(BRAIN_DB)
    
    if args.stats or not any([args.types, args.merge_v, args.noise, args.dedupe, args.all]):
        stats = get_stats(conn)
        print(f"\nGraph Stats")
        print(f"===========")
        print(f"Entities:      {stats['entities']:,}")
        print(f"Relationships: {stats['relationships']:,}")
        print(f"\nTypes:")
        for t, c in stats['types'][:15]:
            print(f"  {t}: {c:,}")
        if len(stats['types']) > 15:
            print(f"  ... and {len(stats['types']) - 15} more types")
        conn.close()
        return
    
    dry_run = args.dry_run
    run_all = args.all
    
    if dry_run:
        print("\n=== DRY RUN MODE (no changes will be made) ===\n")
    
    # 1. Normalize types
    if args.types or run_all:
        print("1. Normalizing entity types...")
        changes = normalize_types(conn, dry_run=dry_run)
        if changes:
            for old, info in changes.items():
                print(f"   {old} -> {info['new_type']} ({info['count']} entities)")
        else:
            print("   No type changes needed")
        print()
    
    # 2. Merge V variants
    if args.merge_v or run_all:
        print("2. Merging V/Vrijen variants...")
        result = merge_v_variants(conn, dry_run=dry_run)
        print(f"   Found {result['merged']} variants: {result.get('variants', [])[:5]}...")
        print(f"   Total mentions: {result.get('total_mentions', 0)}")
        print()
    
    # 3. Find/remove noise
    if args.noise or run_all:
        print("3. Finding noise entities...")
        noise = find_noise_entities(conn)
        print(f"   Found {len(noise)} noise entities")
        if noise[:10]:
            print("   Samples:")
            for n in noise[:10]:
                print(f"     [{n['type']}] {n['name'][:50]}")
        
        if not dry_run and noise:
            noise_ids = [n['id'] for n in noise]
            deleted = delete_noise_entities(conn, noise_ids, dry_run=False)
            print(f"   Deleted {deleted} noise entities")
        print()
    
    # 4. Deduplicate
    if args.dedupe or run_all:
        print("4. Deduplicating entities...")
        result = deduplicate_entities(conn, dry_run=dry_run)
        print(f"   Found {result['duplicates_found']} duplicate groups")
        print(f"   {'Would merge' if dry_run else 'Merged'} {result['entities_merged']} entities")
        print()
    
    # Final stats
    if not dry_run:
        stats = get_stats(conn)
        print(f"Final Stats: {stats['entities']:,} entities, {stats['relationships']:,} relationships")
    
    conn.close()


if __name__ == "__main__":
    main()
