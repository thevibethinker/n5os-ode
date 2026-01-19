#!/usr/bin/env python3
""" 
Deal Signal Router — Worker 1 (Signal Router Core)

Uses unified n5_core.db database with people table and deal_roles junction.

Purpose:
- Accept signals (sms/email/meeting/kondo)
- Match to existing deal (LLM-assisted + heuristic fallback)
- Extract structured intelligence (LLM-assisted + heuristic fallback)
- Update deals and log activities

This module is intentionally "core only": it does NOT require Notion.
Notion sync is handled by Worker 3.

CLI:
  python3 deal_signal_router.py \
    --source sms \
    --content "n5 deal darwinbox They're ready to move forward" \
    --context "careerspan" \
    --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import sys

_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from db_paths import get_db_connection, N5_CORE_DB
from deal_llm_prompts import DEAL_MATCH_PROMPT, SIGNAL_EXTRACTION_PROMPT

CONFIG_PATH_DEFAULT = "/home/workspace/N5/config/deal_signal_config.json"


@dataclass
class DealMatch:
    deal_id: Optional[str]
    person_id: Optional[int]  # Changed from contact_id to person_id
    confidence: int
    match_reason: str


@dataclass
class SignalExtraction:
    stage_signal: str
    inferred_stage: Optional[str]
    stage_change_reason: Optional[str]
    key_facts: List[str]
    next_action: Optional[str]
    next_action_date: Optional[str]
    sentiment: str
    urgency: str


@dataclass
class ProcessResult:
    success: bool
    matched: bool
    deal_id: Optional[str]
    confidence: int
    action_taken: str
    extraction: Optional[SignalExtraction]
    notes: str


def _now_iso() -> str:
    return datetime.now().isoformat()


def _safe_json_loads(text: str) -> Optional[dict]:
    """Parse a JSON object out of an LLM response that may contain extra text."""
    if not text:
        return None

    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except Exception:
            return None

    # Attempt to find first JSON object
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None

    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def _normalize(s: Optional[str]) -> str:
    return (s or "").strip().lower()


def _similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


class DealSignalRouter:
    def __init__(
        self,
        config_path: str = CONFIG_PATH_DEFAULT,
        llm_callable: Optional[Callable[[str], str]] = None,
    ):
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.llm_callable = llm_callable or self._default_llm_callable

    # -------------------------
    # Infrastructure
    # -------------------------

    def _load_config(self, path: str) -> dict:
        p = Path(path)
        if not p.exists():
            # Minimal sane defaults
            return {
                "matching": {"min_confidence_threshold": 70},
                "signals": {
                    "stage_progression": [
                        "identified",
                        "researched",
                        "outreach",
                        "engaged",
                        "qualified",
                        "negotiating",
                        "closed_won",
                    ],
                    "terminal_stages": ["closed_won", "closed_lost"],
                    "auto_advance_signals": {},
                },
            }

        return json.loads(p.read_text())

    def _get_db(self):
        """Get database connection using unified db_paths."""
        return get_db_connection()

    def _default_llm_callable(self, prompt: str) -> str:
        """Best-effort local LLM call wrapper.

        NOTE: Unit tests should inject their own llm_callable.
        """
        try:
            from llm_call import call_llm  # type: ignore
            return call_llm(prompt)
        except Exception:
            try:
                from helpers.llm_helper import call_llm  # type: ignore
                resp = call_llm(prompt, timeout=int(self.config.get("llm", {}).get("timeout_seconds", 30)))
                return resp or ""
            except Exception:
                return ""

    # -------------------------
    # Data Loading
    # -------------------------

    def load_deals(self, limit: Optional[int] = None) -> List[dict]:
        limit_sql = "" if limit is None else f"LIMIT {int(limit)}"
        conn = self._get_db()
        c = conn.cursor()
        c.execute(f"""
            SELECT id, pipeline, company, temperature, stage
            FROM deals
            ORDER BY pipeline, company
            {limit_sql}
        """)
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def load_people_with_roles(self, limit: Optional[int] = None) -> List[dict]:
        """Load people who have deal_roles (linked to deals)."""
        limit_sql = "" if limit is None else f"LIMIT {int(limit)}"
        conn = self._get_db()
        c = conn.cursor()
        c.execute(f"""
            SELECT p.id, p.full_name, p.company, p.email, dr.role, dr.deal_id
            FROM people p
            JOIN deal_roles dr ON p.id = dr.person_id
            ORDER BY p.full_name
            {limit_sql}
        """)
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def get_deal(self, deal_id: str) -> Optional[dict]:
        conn = self._get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM deals WHERE id = ?", (deal_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    # -------------------------
    # LLM + Heuristic: Deal Matching
    # -------------------------

    def match_deal(self, query: str, context: str = "") -> DealMatch:
        deals_limit = int(self.config.get("matching", {}).get("max_deals_to_include", 100))
        people_limit = int(self.config.get("matching", {}).get("max_contacts_to_include", 50))

        deals = self.load_deals(limit=deals_limit)
        people = self.load_people_with_roles(limit=people_limit)

        deal_list = "\n".join([
            f"- {d['id']} | {d['pipeline']} | {d['company']} | stage={d.get('stage') or '-'} | temp={d.get('temperature') or '-'}"
            for d in deals
        ])
        
        # Format people list for LLM (now with deal_id from junction table)
        contact_list = "\n".join([
            f"- person_id={p['id']} | role={p['role']} | {p['full_name']} | {p.get('company') or '-'} | deal_id={p.get('deal_id') or '-'}"
            for p in people
        ])

        prompt = DEAL_MATCH_PROMPT.format(
            query=query,
            context=context,
            deal_list=deal_list,
            contact_list=contact_list,
        )

        llm_data = _safe_json_loads(self.llm_callable(prompt))
        if llm_data and isinstance(llm_data, dict):
            deal_id = llm_data.get("deal_id")
            # Support both contact_id (legacy) and person_id
            person_id = llm_data.get("person_id") or llm_data.get("contact_id")
            try:
                confidence = int(llm_data.get("confidence", 0))
            except Exception:
                confidence = 0
            match_reason = str(llm_data.get("match_reason", ""))

            # If LLM matched person_id but not deal_id, resolve via deal_roles
            if (not deal_id) and person_id:
                for p in people:
                    if p["id"] == person_id and p.get("deal_id"):
                        deal_id = p["deal_id"]
                        if confidence < 85:
                            confidence = max(confidence, 85)
                        match_reason = match_reason or "Matched via person's deal_role"
                        break

            if deal_id or person_id:
                return DealMatch(
                    deal_id=deal_id,
                    person_id=int(person_id) if person_id else None,
                    confidence=max(0, min(100, confidence)),
                    match_reason=match_reason or "LLM match",
                )

        # Heuristic fallback
        return self._match_deal_heuristic(query=query, context=context, deals=deals, people=people)

    def _match_deal_heuristic(self, query: str, context: str, deals: List[dict], people: List[dict]) -> DealMatch:
        q = _normalize(query)
        if not q:
            return DealMatch(None, None, 0, "Empty query")

        # 1) Exact company match
        for d in deals:
            if _normalize(d.get("company")) == q:
                return DealMatch(d["id"], None, 98, "Exact company match")

        # 2) Exact deal id match
        for d in deals:
            if _normalize(d.get("id")) == q:
                return DealMatch(d["id"], None, 98, "Exact deal_id match")

        # 3) Person name match → deal_id via deal_roles
        best_person: Tuple[Optional[dict], float] = (None, 0.0)
        for p in people:
            score = _similarity(q, _normalize(p.get("full_name")))
            if score > best_person[1]:
                best_person = (p, score)

        if best_person[0] and best_person[1] >= 0.86 and best_person[0].get("deal_id"):
            return DealMatch(
                deal_id=best_person[0]["deal_id"],
                person_id=best_person[0]["id"],
                confidence=int(round(best_person[1] * 100)),
                match_reason="Heuristic: person name similarity",
            )

        # 4) Company fuzzy match
        best_deal: Tuple[Optional[dict], float] = (None, 0.0)
        for d in deals:
            score = _similarity(q, _normalize(d.get("company")))
            if score > best_deal[1]:
                best_deal = (d, score)

        if best_deal[0] and best_deal[1] >= 0.78:
            confidence = int(round(best_deal[1] * 100))

            # Context hint bump
            if context and _normalize(best_deal[0].get("pipeline")) == _normalize(context):
                confidence = min(100, confidence + 8)

            return DealMatch(best_deal[0]["id"], None, confidence, "Heuristic: company similarity")

        return DealMatch(None, None, 0, "No match")

    # -------------------------
    # LLM + Heuristic: Signal Extraction
    # -------------------------

    def extract_signal(self, text: str, deal_context: dict) -> SignalExtraction:
        prompt = SIGNAL_EXTRACTION_PROMPT.format(
            text=text,
            company=deal_context.get("company") or "",
            pipeline=deal_context.get("pipeline") or "",
            stage=deal_context.get("stage") or "identified",
            last_touch=deal_context.get("updated_at") or "",  # Changed from last_touched
            temperature=deal_context.get("temperature") or "",
        )

        llm_data = _safe_json_loads(self.llm_callable(prompt))
        if llm_data and isinstance(llm_data, dict):
            return self._coerce_signal_extraction(llm_data, fallback_text=text, deal_context=deal_context)

        # Heuristic fallback
        return self._extract_signal_heuristic(text=text, deal_context=deal_context)

    def _coerce_signal_extraction(self, data: dict, fallback_text: str, deal_context: dict) -> SignalExtraction:
        def _as_list(v: Any) -> List[str]:
            if isinstance(v, list):
                return [str(x).strip() for x in v if str(x).strip()]
            return []

        stage_signal = str(data.get("stage_signal", "none"))
        inferred_stage = data.get("inferred_stage")
        inferred_stage = str(inferred_stage).strip() if inferred_stage else None

        return SignalExtraction(
            stage_signal=stage_signal,
            inferred_stage=inferred_stage,
            stage_change_reason=(str(data.get("stage_change_reason")).strip() if data.get("stage_change_reason") else None),
            key_facts=_as_list(data.get("key_facts")),
            next_action=(str(data.get("next_action")).strip() if data.get("next_action") else None),
            next_action_date=(str(data.get("next_action_date")).strip() if data.get("next_action_date") else None),
            sentiment=str(data.get("sentiment", "neutral")),
            urgency=str(data.get("urgency", "medium")),
        )

    def _extract_signal_heuristic(self, text: str, deal_context: dict) -> SignalExtraction:
        t = _normalize(text)
        current_stage = _normalize(deal_context.get("stage") or "identified")

        stage_progression: List[str] = self.config.get("signals", {}).get(
            "stage_progression",
            ["identified", "researched", "outreach", "engaged", "qualified", "negotiating", "closed_won"],
        )
        terminal = set(self.config.get("signals", {}).get("terminal_stages", ["closed_won", "closed_lost"]))
        signals_map: Dict[str, List[str]] = self.config.get("signals", {}).get("auto_advance_signals", {})

        inferred: Optional[str] = None
        for stage, keywords in signals_map.items():
            for kw in keywords:
                if kw and kw.lower() in t:
                    inferred = stage
                    break
            if inferred:
                break

        # Sentiment quick pass
        sentiment = "neutral"
        if any(w in t for w in ["excited", "interested", "ready", "great", "yes", "positive"]):
            sentiment = "positive"
        if any(w in t for w in ["declined", "no", "not interested", "passed", "dead"]):
            sentiment = "negative"

        urgency = "medium"
        if any(w in t for w in ["asap", "urgent", "today", "tomorrow"]):
            urgency = "high"

        # Stage change logic
        stage_signal = "none"
        stage_change_reason = None

        if inferred and current_stage not in terminal:
            try:
                cur_idx = stage_progression.index(current_stage)
            except ValueError:
                cur_idx = 0

            if inferred == "closed_lost":
                stage_signal = "stage_change"
                stage_change_reason = "Heuristic: decline/pass keywords"
            elif inferred in stage_progression:
                inf_idx = stage_progression.index(inferred)
                if inf_idx > cur_idx:
                    stage_signal = "stage_change"
                    stage_change_reason = "Heuristic: keyword-based stage advance"
                else:
                    inferred = None

        # Next action heuristic: look for "need to" / "next" patterns
        next_action = None
        m = re.search(r"\b(need to|next|action|follow up)[:\s]+([^\n\.]{8,120})", text, re.IGNORECASE)
        if m:
            next_action = m.group(2).strip()

        key_facts: List[str] = []
        # Simple: extract up to 2 sentences containing numbers or dates-ish
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for s in sentences:
            if len(key_facts) >= 2:
                break
            if re.search(r"\b\d{1,4}\b", s) or re.search(r"\b(q[1-4]|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b", s, re.IGNORECASE):
                key_facts.append(s.strip()[:200])

        return SignalExtraction(
            stage_signal=stage_signal,
            inferred_stage=inferred,
            stage_change_reason=stage_change_reason,
            key_facts=key_facts,
            next_action=next_action,
            next_action_date=None,
            sentiment=sentiment,
            urgency=urgency,
        )

    # -------------------------
    # Apply Updates
    # -------------------------

    def process_signal(self, source: str, content: str, metadata: Optional[dict] = None, context: str = "", dry_run: bool = False) -> ProcessResult:
        metadata = metadata or {}

        query = content
        match = self.match_deal(query=query, context=context)

        min_conf = int(self.config.get("matching", {}).get("min_confidence_threshold", 70))
        if not match.deal_id or match.confidence < min_conf:
            return ProcessResult(
                success=True,
                matched=False,
                deal_id=None,
                confidence=match.confidence,
                action_taken="unknown_signal",
                extraction=None,
                notes=f"No deal match (confidence={match.confidence}). Reason: {match.match_reason}",
            )

        deal = self.get_deal(match.deal_id)
        if not deal:
            return ProcessResult(
                success=False,
                matched=True,
                deal_id=match.deal_id,
                confidence=match.confidence,
                action_taken="error",
                extraction=None,
                notes="Matched deal_id but deal not found in DB",
            )

        extraction = self.extract_signal(text=content, deal_context=deal)

        if dry_run:
            return ProcessResult(
                success=True,
                matched=True,
                deal_id=match.deal_id,
                confidence=match.confidence,
                action_taken="dry_run",
                extraction=extraction,
                notes="Dry run: no DB changes",
            )

        self._apply_update(deal=deal, source=source, content=content, extraction=extraction, metadata=metadata)

        return ProcessResult(
            success=True,
            matched=True,
            deal_id=match.deal_id,
            confidence=match.confidence,
            action_taken="updated",
            extraction=extraction,
            notes="Updated n5_core.db + logged activity",
        )

    def _apply_update(self, deal: dict, source: str, content: str, extraction: SignalExtraction, metadata: dict):
        conn = self._get_db()
        c = conn.cursor()

        now = _now_iso()

        updates: Dict[str, Any] = {}

        if extraction.inferred_stage:
            updates["stage"] = extraction.inferred_stage

        # Note: new schema doesn't have next_action column - store in notes
        if extraction.next_action:
            existing_notes = deal.get("notes") or ""
            action_note = f"\n[{now[:10]}] Next action: {extraction.next_action}"
            updates["notes"] = (existing_notes + action_note).strip()

        # Apply deal update if there are changes
        if updates:
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            params = list(updates.values()) + [deal["id"]]
            c.execute(f"UPDATE deals SET {set_clause} WHERE id = ?", params)

        # Log activity using deal_activities table
        activity_desc = {
            "source": source,
            "content": content,
            "extraction": {
                "stage_signal": extraction.stage_signal,
                "inferred_stage": extraction.inferred_stage,
                "key_facts": extraction.key_facts,
                "next_action": extraction.next_action,
                "sentiment": extraction.sentiment,
                "urgency": extraction.urgency,
            },
            "metadata": metadata,
            "timestamp": now,
        }

        c.execute("""
            INSERT INTO deal_activities (deal_id, activity_type, description, performed_by, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            deal["id"],
            "note",
            json.dumps(activity_desc, ensure_ascii=False),
            source,
            now,
        ))

        # Also log stage change as separate activity (useful for dashboards)
        if extraction.inferred_stage and _normalize(extraction.inferred_stage) != _normalize(deal.get("stage")):
            c.execute("""
                INSERT INTO deal_activities (deal_id, activity_type, description, performed_by, timestamp)
                VALUES (?, 'stage_change', ?, ?, ?)
            """, (
                deal["id"],
                f"Stage changed to: {extraction.inferred_stage}. Reason: {extraction.stage_change_reason or ''}".strip(),
                source,
                now,
            ))

        conn.commit()
        conn.close()


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Deal Signal Router")
    p.add_argument("--source", required=True, choices=["sms", "email", "meeting", "kondo"], help="Signal source")
    p.add_argument("--content", required=True, help="Signal content text")
    p.add_argument("--context", default="", help="Pipeline context hint (careerspan|zo)")
    p.add_argument("--dry-run", action="store_true", help="Do not write to DB")
    p.add_argument("--config", default=CONFIG_PATH_DEFAULT, help="Path to deal signal config")
    return p.parse_args()


def main():
    args = _parse_args()
    router = DealSignalRouter(config_path=args.config)
    result = router.process_signal(source=args.source, content=args.content, context=args.context, dry_run=args.dry_run)
    print(json.dumps(result.__dict__, indent=2, default=str))


if __name__ == "__main__":
    main()
