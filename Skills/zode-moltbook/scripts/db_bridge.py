#!/usr/bin/env python3
"""
DB Bridge — Interface to social_intelligence.db for all Zøde scripts.

Provides read/write access to agents, concepts, threads, comments,
and interaction tracking. This is the SSOT for Zøde's social intelligence.

Usage:
    from db_bridge import SocialDB
    db = SocialDB()
    db.upsert_agent(agent_id="abc", display_name="Duncan", ...)
    db.log_interaction(from_agent="zode", to_agent="abc", ...)
    db.close()
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Resolve DB path relative to this script's location
_SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH = _SCRIPT_DIR.parent / "state" / "social_intelligence.db"

# Lazy import — duckdb may not be available in all contexts
_duckdb = None


def _get_duckdb():
    global _duckdb
    if _duckdb is None:
        import duckdb
        _duckdb = duckdb
    return _duckdb


ZODE_AGENT_ID = "69b73ef4-909b-44c5-8d6e-ac1153c2b346"


class SocialDB:
    """Interface to Zøde's social intelligence database."""

    def __init__(self, read_only: bool = False):
        duckdb = _get_duckdb()
        self.db = duckdb.connect(str(DB_PATH), read_only=read_only)
        if not read_only:
            self._ensure_schema_extensions()

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _ensure_schema_extensions(self):
        """Add columns introduced by feed-reactive content system. Safe to call repeatedly."""
        for col, typedef in [
            ("lens_used", "VARCHAR DEFAULT ''"),
            ("discourse_topic", "VARCHAR DEFAULT ''"),
        ]:
            try:
                self.db.execute(f"ALTER TABLE our_posts ADD COLUMN {col} {typedef}")
            except Exception:
                pass  # Column already exists

    # --- Agents ---

    def upsert_agent(
        self,
        agent_id: str,
        display_name: str,
        karma: int = 0,
        followers: int = 0,
        category: str = "soft_power",
        engagement_quality: str = "contributor",
        relevance: str = "medium",
        notes: str = "",
        zode_relationship: str = "none",
    ):
        """Insert or update an agent record."""
        now = datetime.now(timezone.utc).isoformat()
        existing = self.db.execute(
            "SELECT agent_id FROM agents WHERE agent_id = ?", [agent_id]
        ).fetchone()

        if existing:
            self.db.execute("""
                UPDATE agents SET
                    display_name = COALESCE(?, display_name),
                    karma = ?,
                    followers = ?,
                    category = COALESCE(?, category),
                    engagement_quality = COALESCE(?, engagement_quality),
                    relevance = COALESCE(?, relevance),
                    notes = CASE WHEN ? != '' THEN ? ELSE notes END,
                    zode_relationship = CASE WHEN ? != 'none' THEN ? ELSE zode_relationship END,
                    last_seen = ?
                WHERE agent_id = ?
            """, [display_name, karma, followers, category, engagement_quality,
                  relevance, notes, notes, zode_relationship, zode_relationship,
                  now, agent_id])
        else:
            self.db.execute("""
                INSERT INTO agents (agent_id, display_name, karma, followers,
                    category, engagement_quality, relevance, notes,
                    zode_relationship, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [agent_id, display_name, karma, followers, category,
                  engagement_quality, relevance, notes, zode_relationship, now, now])

    def get_agent(self, agent_id: str) -> dict | None:
        """Get an agent by ID."""
        row = self.db.execute(
            "SELECT * FROM agents WHERE agent_id = ?", [agent_id]
        ).fetchone()
        if not row:
            return None
        cols = [d[0] for d in self.db.description]
        return dict(zip(cols, row))

    def get_agents_by_relationship(self, relationship: str) -> list[dict]:
        """Get all agents with a specific relationship to Zøde."""
        rows = self.db.execute(
            "SELECT * FROM agents WHERE zode_relationship = ? ORDER BY karma DESC",
            [relationship]
        ).fetchall()
        cols = [d[0] for d in self.db.description]
        return [dict(zip(cols, row)) for row in rows]

    def list_agents(self, limit: int = 50) -> list[dict]:
        """List agents ordered by relevance then karma."""
        rows = self.db.execute("""
            SELECT * FROM agents
            ORDER BY
                CASE relevance
                    WHEN 'very_high' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                    ELSE 5
                END,
                karma DESC
            LIMIT ?
        """, [limit]).fetchall()
        cols = [d[0] for d in self.db.description]
        return [dict(zip(cols, row)) for row in rows]

    # --- Concepts ---

    def get_concept(self, name: str) -> dict | None:
        """Get a concept by name."""
        row = self.db.execute(
            "SELECT * FROM concepts WHERE name = ?", [name]
        ).fetchone()
        if not row:
            return None
        cols = [d[0] for d in self.db.description]
        return dict(zip(cols, row))

    def increment_concept_reference(self, name: str):
        """Increment the reference count for a concept."""
        self.db.execute(
            "UPDATE concepts SET times_referenced = times_referenced + 1 WHERE name = ?",
            [name]
        )

    def record_concept_adoption(
        self, agent_id: str, concept_name: str, context: str,
        adoption_type: str = "paraphrased"
    ):
        """Record that an agent used one of Zøde's concepts."""
        concept = self.get_concept(concept_name)
        if not concept:
            return
        self.db.execute("""
            INSERT INTO concept_adoption (id, agent_id, concept_id, context, adoption_type)
            VALUES (nextval('adoption_seq'), ?, ?, ?, ?)
        """, [agent_id, concept["concept_id"], context, adoption_type])
        # Increment adoption count
        self.db.execute(
            "UPDATE concepts SET times_adopted = times_adopted + 1 WHERE concept_id = ?",
            [concept["concept_id"]]
        )

    def list_concepts(self) -> list[dict]:
        """List all concepts ordered by adoption count."""
        rows = self.db.execute("""
            SELECT * FROM concepts ORDER BY times_adopted DESC, times_referenced DESC
        """).fetchall()
        cols = [d[0] for d in self.db.description]
        return [dict(zip(cols, row)) for row in rows]

    # --- Threads ---

    def upsert_thread(
        self, post_id: str, title: str, author_agent_id: str = None,
        submolt: str = "general", upvotes: int = 0, comment_count: int = 0,
        our_engagement: str = "none", strategic_value: str = "medium",
        notes: str = ""
    ):
        """Insert or update a thread we're tracking."""
        existing = self.db.execute(
            "SELECT post_id FROM threads WHERE post_id = ?", [post_id]
        ).fetchone()
        now = datetime.now(timezone.utc).isoformat()

        if existing:
            self.db.execute("""
                UPDATE threads SET
                    upvotes = ?, comment_count = ?,
                    our_engagement = CASE WHEN ? != 'none' THEN ? ELSE our_engagement END,
                    engagement_date = CASE WHEN ? != 'none' THEN ? ELSE engagement_date END,
                    notes = CASE WHEN ? != '' THEN ? ELSE notes END
                WHERE post_id = ?
            """, [upvotes, comment_count, our_engagement, our_engagement,
                  our_engagement, now, notes, notes, post_id])
        else:
            self.db.execute("""
                INSERT INTO threads (post_id, title, author_agent_id, submolt,
                    upvotes, comment_count, our_engagement, engagement_date,
                    strategic_value, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [post_id, title, author_agent_id, submolt, upvotes,
                  comment_count, our_engagement, now, strategic_value, notes])

    # --- Our Comments ---

    def record_our_comment(
        self, comment_id: str, post_id: str, content: str,
        concepts_used: list[str] = None, target_agent: str = None,
        strategic_intent: str = ""
    ):
        """Record a comment Zøde has posted."""
        existing = self.db.execute(
            "SELECT comment_id FROM our_comments WHERE comment_id = ?", [comment_id]
        ).fetchone()
        if existing:
            return  # Already tracked

        concepts_json = json.dumps(concepts_used or [])
        self.db.execute("""
            INSERT INTO our_comments (comment_id, post_id, content, concepts_used,
                target_agent, strategic_intent)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [comment_id, post_id, content, concepts_json, target_agent, strategic_intent])

    # --- Our Posts ---

    def record_our_post(
        self, post_id: str, title: str, submolt: str = "general",
        content: str = "", concepts_introduced: list[str] = None,
        posted_at: str = None
    ):
        """Record a post Zøde has published. Skips if already tracked."""
        existing = self.db.execute(
            "SELECT post_id FROM our_posts WHERE post_id = ?", [post_id]
        ).fetchone()
        if existing:
            return  # Already tracked

        concepts_json = json.dumps(concepts_introduced or [])
        ts = posted_at or datetime.now(timezone.utc).isoformat()
        self.db.execute("""
            INSERT INTO our_posts (post_id, title, submolt, content,
                concepts_introduced, posted_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [post_id, title, submolt, content, concepts_json, ts])

    def update_our_post_metrics(self, post_id: str, upvotes: int, downvotes: int, comment_count: int):
        """Update metrics for one of our posts."""
        self.db.execute("""
            UPDATE our_posts SET upvotes = ?, downvotes = ?, comment_count = ?
            WHERE post_id = ?
        """, [upvotes, downvotes, comment_count, post_id])

    # --- Interactions ---

    def log_interaction(
        self, from_agent: str, to_agent: str, interaction_type: str,
        context_id: str = "", notes: str = ""
    ):
        """Log an agent-to-agent interaction."""
        self.db.execute("""
            INSERT INTO agent_interactions (id, from_agent, to_agent,
                interaction_type, context_id, notes)
            VALUES (nextval('interaction_seq'), ?, ?, ?, ?, ?)
        """, [from_agent, to_agent, interaction_type, context_id, notes])

    def get_interactions_with(self, agent_id: str) -> list[dict]:
        """Get all interactions involving an agent."""
        rows = self.db.execute("""
            SELECT * FROM agent_interactions
            WHERE from_agent = ? OR to_agent = ?
            ORDER BY observed_at DESC
        """, [agent_id, agent_id]).fetchall()
        cols = [d[0] for d in self.db.description]
        return [dict(zip(cols, row)) for row in rows]

    # --- Summary Queries ---

    def engagement_summary(self) -> dict:
        """Get a summary of Zøde's engagement activity."""
        posts = self.db.execute("SELECT COUNT(*) FROM our_posts").fetchone()[0]
        comments = self.db.execute("SELECT COUNT(*) FROM our_comments").fetchone()[0]
        agents_engaged = self.db.execute(
            "SELECT COUNT(*) FROM agents WHERE zode_relationship != 'none' AND zode_relationship != 'self'"
        ).fetchone()[0]
        concepts_coined = self.db.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]
        concepts_adopted = self.db.execute(
            "SELECT COUNT(*) FROM concepts WHERE times_adopted > 0"
        ).fetchone()[0]
        interactions = self.db.execute("SELECT COUNT(*) FROM agent_interactions").fetchone()[0]

        return {
            "posts": posts,
            "comments": comments,
            "agents_engaged": agents_engaged,
            "concepts_coined": concepts_coined,
            "concepts_adopted": concepts_adopted,
            "interactions": interactions,
        }

    def concept_leaderboard(self) -> list[dict]:
        """Show which concepts are getting traction."""
        rows = self.db.execute("""
            SELECT name, times_referenced, times_adopted, status
            FROM concepts
            ORDER BY times_adopted DESC, times_referenced DESC
        """).fetchall()
        return [{"name": r[0], "referenced": r[1], "adopted": r[2], "status": r[3]} for r in rows]

    def repeater_candidates(self) -> list[dict]:
        """Find agents most likely to become repeaters of Zøde's concepts."""
        rows = self.db.execute("""
            SELECT a.agent_id, a.display_name, a.karma, a.relevance,
                   a.zode_relationship, COUNT(i.id) as interaction_count
            FROM agents a
            LEFT JOIN agent_interactions i
                ON (i.from_agent = a.agent_id OR i.to_agent = a.agent_id)
                AND (i.from_agent = ? OR i.to_agent = ?)
            WHERE a.agent_id != ?
                AND a.zode_relationship IN ('engaged', 'replied_to_us')
            GROUP BY a.agent_id, a.display_name, a.karma, a.relevance, a.zode_relationship
            ORDER BY interaction_count DESC, a.karma DESC
        """, [ZODE_AGENT_ID, ZODE_AGENT_ID, ZODE_AGENT_ID]).fetchall()
        return [
            {"agent_id": r[0], "name": r[1], "karma": r[2], "relevance": r[3],
             "relationship": r[4], "interactions": r[5]}
            for r in rows
        ]

    # --- Epistemic Intelligence ---

    def upsert_idea(
        self, idea_id: str, name: str, description: str = "",
        category: str = "general", introduced_by: str = None,
        introduced_in: str = None, zode_stance: str = "neutral",
        related_concepts: list[str] = None, tags: list[str] = None
    ):
        """Insert or update an idea in the epistemic layer."""
        now = datetime.now(timezone.utc).isoformat()
        existing = self.db.execute(
            "SELECT idea_id FROM ideas WHERE idea_id = ?", [idea_id]
        ).fetchone()

        concepts_json = json.dumps(related_concepts or [])
        tags_json = json.dumps(tags or [])

        if existing:
            self.db.execute("""
                UPDATE ideas SET
                    name = COALESCE(?, name),
                    description = CASE WHEN ? != '' THEN ? ELSE description END,
                    category = COALESCE(?, category),
                    zode_stance = CASE WHEN ? != 'neutral' THEN ? ELSE zode_stance END,
                    related_concepts = CASE WHEN ? != '[]' THEN ? ELSE related_concepts END,
                    tags = CASE WHEN ? != '[]' THEN ? ELSE tags END
                WHERE idea_id = ?
            """, [name, description, description, category,
                  zode_stance, zode_stance, concepts_json, concepts_json,
                  tags_json, tags_json, idea_id])
        else:
            self.db.execute("""
                INSERT INTO ideas (idea_id, name, description, category,
                    introduced_by, introduced_in, introduced_date,
                    zode_stance, related_concepts, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [idea_id, name, description, category, introduced_by,
                  introduced_in, now, zode_stance, concepts_json, tags_json])

    def get_idea(self, idea_id: str) -> dict | None:
        """Get an idea by ID."""
        row = self.db.execute(
            "SELECT * FROM ideas WHERE idea_id = ?", [idea_id]
        ).fetchone()
        if not row:
            return None
        cols = [d[0] for d in self.db.description]
        return dict(zip(cols, row))

    def list_ideas(self, category: str = None, status: str = "active") -> list[dict]:
        """List ideas, optionally filtered."""
        if category:
            rows = self.db.execute(
                "SELECT * FROM ideas WHERE status = ? AND category = ? ORDER BY introduced_date DESC",
                [status, category]
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT * FROM ideas WHERE status = ? ORDER BY introduced_date DESC",
                [status]
            ).fetchall()
        cols = [d[0] for d in self.db.description]
        return [dict(zip(cols, row)) for row in rows]

    def record_position(
        self, agent_id: str, idea_id: str, stance: str,
        evidence: str = "", context_post_id: str = "",
        confidence: str = "medium"
    ):
        """Record an agent's position on an idea.

        stance: 'agrees', 'disagrees', 'extends', 'qualifies', 'neutral'
        """
        self.db.execute("""
            INSERT INTO positions (id, agent_id, idea_id, stance,
                evidence, context_post_id, confidence)
            VALUES (nextval('position_seq'), ?, ?, ?, ?, ?, ?)
        """, [agent_id, idea_id, stance, evidence, context_post_id, confidence])

    def get_positions_on(self, idea_id: str) -> list[dict]:
        """Get all agent positions on an idea."""
        rows = self.db.execute("""
            SELECT p.*, a.display_name as agent_name
            FROM positions p
            LEFT JOIN agents a ON p.agent_id = a.agent_id
            WHERE p.idea_id = ?
            ORDER BY p.observed_at DESC
        """, [idea_id]).fetchall()
        cols = [d[0] for d in self.db.description]
        return [dict(zip(cols, row)) for row in rows]

    def upsert_discourse(
        self, thread_id: str, topic: str, related_ideas: list[str] = None,
        started_by: str = None, post_ids: list[str] = None,
        participant_count: int = 0, zode_engaged: bool = False,
        notes: str = ""
    ):
        """Track an ongoing discourse thread spanning multiple posts."""
        now = datetime.now(timezone.utc).isoformat()
        ideas_json = json.dumps(related_ideas or [])
        posts_json = json.dumps(post_ids or [])

        existing = self.db.execute(
            "SELECT thread_id FROM discourse_threads WHERE thread_id = ?", [thread_id]
        ).fetchone()

        if existing:
            self.db.execute("""
                UPDATE discourse_threads SET
                    topic = COALESCE(?, topic),
                    related_ideas = CASE WHEN ? != '[]' THEN ? ELSE related_ideas END,
                    last_activity = ?,
                    post_ids = CASE WHEN ? != '[]' THEN ? ELSE post_ids END,
                    participant_count = CASE WHEN ? > 0 THEN ? ELSE participant_count END,
                    zode_engaged = CASE WHEN ? THEN true ELSE zode_engaged END,
                    notes = CASE WHEN ? != '' THEN ? ELSE notes END
                WHERE thread_id = ?
            """, [topic, ideas_json, ideas_json, now, posts_json, posts_json,
                  participant_count, participant_count, zode_engaged,
                  notes, notes, thread_id])
        else:
            self.db.execute("""
                INSERT INTO discourse_threads (thread_id, topic, related_ideas,
                    started_by, started_at, last_activity, post_ids,
                    participant_count, zode_engaged, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [thread_id, topic, ideas_json, started_by, now, now,
                  posts_json, participant_count, zode_engaged, notes])

    def record_idea_lineage(
        self, source_idea: str, target_idea: str,
        relationship: str, context_post_id: str = "",
        notes: str = ""
    ):
        """Record how one idea relates to another.

        relationship: 'extends', 'challenges', 'refines', 'synthesizes', 'contradicts'
        """
        self.db.execute("""
            INSERT INTO idea_lineage (id, source_idea, target_idea,
                relationship, context_post_id, notes)
            VALUES (nextval('lineage_seq'), ?, ?, ?, ?, ?)
        """, [source_idea, target_idea, relationship, context_post_id, notes])

    def idea_landscape(self) -> dict:
        """Get a summary of the epistemic landscape."""
        ideas_count = self.db.execute("SELECT COUNT(*) FROM ideas WHERE status = 'active'").fetchone()[0]
        positions_count = self.db.execute("SELECT COUNT(*) FROM positions").fetchone()[0]
        discourses = self.db.execute("SELECT COUNT(*) FROM discourse_threads WHERE status = 'active'").fetchone()[0]
        lineages = self.db.execute("SELECT COUNT(*) FROM idea_lineage").fetchone()[0]

        # Ideas by category
        cats = self.db.execute("""
            SELECT category, COUNT(*) as cnt FROM ideas
            WHERE status = 'active' GROUP BY category ORDER BY cnt DESC
        """).fetchall()

        # Ideas with most positions (contested/discussed)
        hot = self.db.execute("""
            SELECT i.name, COUNT(p.id) as position_count
            FROM ideas i JOIN positions p ON i.idea_id = p.idea_id
            GROUP BY i.name ORDER BY position_count DESC LIMIT 5
        """).fetchall()

        return {
            "ideas": ideas_count,
            "positions": positions_count,
            "active_discourses": discourses,
            "idea_lineages": lineages,
            "categories": {r[0]: r[1] for r in cats},
            "most_discussed": [{"idea": r[0], "positions": r[1]} for r in hot],
        }

    # --- Export for compatibility ---

    def export_agents_jsonl(self) -> str:
        """Export agents table as JSONL (for backward compatibility with agents.jsonl)."""
        agents = self.list_agents(limit=500)
        lines = []
        for a in agents:
            # Convert to the old agents.jsonl format
            entry = {
                "name": a["display_name"],
                "karma": a["karma"],
                "followers": a["followers"],
                "registered": str(a.get("registered_date", "")),
                "relevance": a["relevance"],
                "category": a["category"],
                "engagement_quality": a["engagement_quality"],
                "notes": a["notes"] or "",
                "zode_relationship": a["zode_relationship"],
                "observed_at": str(a.get("last_seen", "")),
            }
            lines.append(json.dumps(entry))
        return "\n".join(lines) + "\n" if lines else ""


# --- CLI ---

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Social Intelligence DB Bridge")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("summary", help="Show engagement summary")
    sub.add_parser("concepts", help="Show concept leaderboard")
    sub.add_parser("repeaters", help="Show repeater candidates")
    sub.add_parser("agents", help="List agents")
    sub.add_parser("ideas", help="List tracked ideas")
    sub.add_parser("landscape", help="Show epistemic landscape summary")
    sub.add_parser("export-agents", help="Export agents as JSONL (compatibility)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    with SocialDB(read_only=True) as db:
        if args.command == "summary":
            s = db.engagement_summary()
            print("ZØDE ENGAGEMENT SUMMARY")
            print("=" * 40)
            for k, v in s.items():
                print(f"  {k}: {v}")
            # Add epistemic summary
            e = db.idea_landscape()
            print()
            print("EPISTEMIC LANDSCAPE")
            print("=" * 40)
            print(f"  Ideas tracked: {e['ideas']}")
            print(f"  Agent positions: {e['positions']}")
            print(f"  Active discourses: {e['active_discourses']}")
            print(f"  Idea lineages: {e['idea_lineages']}")
            if e['categories']:
                print(f"  Categories: {e['categories']}")
            if e['most_discussed']:
                print("  Most discussed:")
                for m in e['most_discussed']:
                    print(f"    → {m['idea']}: {m['positions']} positions")

        elif args.command == "concepts":
            concepts = db.concept_leaderboard()
            print("CONCEPT LEADERBOARD")
            print("=" * 40)
            for c in concepts:
                print(f"  [{c['status']}] {c['name']}: {c['referenced']} refs, {c['adopted']} adoptions")

        elif args.command == "repeaters":
            reps = db.repeater_candidates()
            print("REPEATER CANDIDATES")
            print("=" * 40)
            for r in reps:
                print(f"  {r['name']} (karma:{r['karma']}) — {r['relationship']}, {r['interactions']} interactions")

        elif args.command == "agents":
            agents = db.list_agents()
            for a in agents:
                print(f"  [{a['relevance']}] {a['display_name']} (karma:{a['karma']}) — {a['zode_relationship']}")

        elif args.command == "ideas":
            ideas = db.list_ideas()
            if not ideas:
                print("No ideas tracked yet.")
            else:
                print("TRACKED IDEAS")
                print("=" * 40)
                for idea in ideas:
                    stance_tag = f" [Zøde: {idea['zode_stance']}]" if idea.get('zode_stance') != 'neutral' else ""
                    print(f"  [{idea['category']}] {idea['name']}{stance_tag}")
                    if idea.get('description'):
                        print(f"    {idea['description'][:80]}")

        elif args.command == "landscape":
            e = db.idea_landscape()
            print("EPISTEMIC LANDSCAPE")
            print("=" * 40)
            print(f"  Ideas tracked: {e['ideas']}")
            print(f"  Agent positions: {e['positions']}")
            print(f"  Active discourses: {e['active_discourses']}")
            print(f"  Idea lineages: {e['idea_lineages']}")
            if e['categories']:
                print(f"  Categories: {e['categories']}")
            if e['most_discussed']:
                print("  Most discussed:")
                for m in e['most_discussed']:
                    print(f"    → {m['idea']}: {m['positions']} positions")

        elif args.command == "export-agents":
            print(db.export_agents_jsonl())


if __name__ == "__main__":
    main()
