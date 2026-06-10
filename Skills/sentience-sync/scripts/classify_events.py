#!/usr/bin/env python3
"""
Layered event classifier for Sentience CRM pipeline.

Replaces the keyword-only classifier in daily_digest.py with a multi-signal
scoring system that evaluates source, entity, keyword, domain, and context
layers. Routes weak evidence to 'uncertain' instead of forcing confident buckets.

Usage:
    # Classify a single event (JSON on stdin)
    echo '{"event_id":"...","source_type":"desktop",...}' | python3 classify_events.py

    # Classify a batch from activity_feed.jsonl (raw Sentience format)
    python3 classify_events.py --feed data/activity_feed.jsonl

    # Classify normalized events from a file
    python3 classify_events.py --normalized events.jsonl

    # Run eval against labeled examples
    python3 classify_events.py --eval artifacts/eval-set.jsonl

    # Show detailed scoring breakdown
    python3 classify_events.py --feed data/activity_feed.jsonl --verbose
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from normalize import normalize

SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
RUBRIC_FILE = DATA_DIR / "relevance_rubric.yaml"
CONTACT_INDEX_FILE = Path("/home/workspace/Skills/sentience-sync/data/local_contact_index.json")

OWNER_NAMES = {"primary user", "primary", "primary user"}


@dataclass
class SignalHit:
    layer: str       # source | entity | keyword | domain | context
    bucket: str
    detail: str
    weight: float


@dataclass
class ClassificationResult:
    bucket: str
    confidence: float
    priority: str
    signals: list[SignalHit] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    uncertain: bool = False
    candidate_buckets: list[str] = field(default_factory=list)
    uncertainty_reason: str = ""
    layers_fired: set[str] = field(default_factory=set)


class LayeredClassifier:

    def __init__(self, rubric_path: Path | None = None, contact_index_path: Path | None = None):
        self._rubric = self._load_rubric(rubric_path or RUBRIC_FILE)
        self._contact_index = self._load_contact_index(contact_index_path or CONTACT_INDEX_FILE)
        self._neutral_apps = set(
            a.casefold() for a in self._rubric.get("neutral_apps", [])
        )
        self._thresholds = self._rubric.get("thresholds", {})
        self._min_score = self._thresholds.get("min_bucket_score", 3)
        self._ambiguity_ratio = self._thresholds.get("ambiguity_ratio", 0.8)
        self._keyword_only_penalty = self._thresholds.get("keyword_only_penalty", 0.5)
        self._entity_name_index = self._build_entity_name_index()
        self._entity_company_index = self._build_entity_company_index()
        self._priority_patterns = self._compile_priority_patterns()

    # ── Loading ──────────────────────────────────────────────────────

    @staticmethod
    def _load_rubric(path: Path) -> dict:
        try:
            return yaml.safe_load(path.read_text())
        except Exception as e:
            print(f"ERROR loading rubric: {e}", file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def _load_contact_index(path: Path) -> dict:
        try:
            return json.loads(path.read_text())
        except FileNotFoundError:
            return {"people": [], "companies": []}
        except Exception:
            return {"people": [], "companies": []}

    def _build_entity_name_index(self) -> dict[str, list[str]]:
        """Map lowercase person names to their bucket affiliations."""
        index: dict[str, list[str]] = {}
        rubric_buckets = self._rubric.get("buckets", {})
        for bucket_name, config in rubric_buckets.items():
            if bucket_name == "other":
                continue
            signals = config.get("signals", {})
            entity_cfg = signals.get("entity", {})
            for person in entity_cfg.get("people", []):
                key = person.casefold()
                if key not in OWNER_NAMES:
                    index.setdefault(key, []).append(bucket_name)
        company_bucket = self._build_contact_company_bucket_map()
        for person in self._contact_index.get("people", []):
            first = (person.get("first_name") or "").strip()
            last = (person.get("last_name") or "").strip()
            full = f"{first} {last}".strip().casefold()
            if not full or full in OWNER_NAMES:
                continue
            comp_id = person.get("company")
            if comp_id and comp_id in company_bucket:
                bucket = company_bucket[comp_id]
                index.setdefault(full, []).append(bucket)
                if first:
                    index.setdefault(first, []).append(bucket)
        return index

    def _build_entity_company_index(self) -> dict[str, list[str]]:
        """Map lowercase company names to their bucket affiliations."""
        index: dict[str, list[str]] = {}
        rubric_buckets = self._rubric.get("buckets", {})
        for bucket_name, config in rubric_buckets.items():
            if bucket_name == "other":
                continue
            signals = config.get("signals", {})
            entity_cfg = signals.get("entity", {})
            for company in entity_cfg.get("companies", []):
                key = company.casefold()
                index.setdefault(key, []).append(bucket_name)
        for comp in self._contact_index.get("companies", []):
            name = (comp.get("name") or "").strip().casefold()
            if not name:
                continue
            domain = (comp.get("domain") or "").strip().lower()
            cid = comp.get("id", "")
            bucket = self._local_id_to_bucket(cid)
            if bucket:
                index.setdefault(name, []).append(bucket)
                if domain:
                    index.setdefault(domain, []).append(bucket)
        return index

    def _build_contact_company_bucket_map(self) -> dict[str, str]:
        """Map local company IDs to bucket names."""
        mapping: dict[str, str] = {}
        entity_map = self._rubric.get("entity_bucket_map", {})
        for bucket_name, config in entity_map.items():
            for cid in config.get("local_company_ids", []):
                mapping[cid] = bucket_name
        return mapping

    def _local_id_to_bucket(self, company_id: str) -> str | None:
        mapping = self._build_contact_company_bucket_map()
        return mapping.get(company_id)

    # ── Priority patterns ────────────────────────────────────────────

    @staticmethod
    def _compile_priority_patterns() -> dict[str, list[re.Pattern]]:
        return {
            "HIGH": [
                re.compile(r"\b(?:agreed to|committed to|i will|we will|i'll|we'll)\b", re.I),
                re.compile(r"\b(?:by|before)\s+(?:tomorrow|tonight|eod|eow|end of|next week|this week|monday|tuesday|wednesday|thursday|friday)\b", re.I),
                re.compile(r"\b(?:by|before)\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)\b", re.I),
                re.compile(r"\bdeadline\b(?!\s*(?:not|no|without|free))", re.I),
                re.compile(r"\baction item\b", re.I),
                re.compile(r"\bscheduled\s+(?:a\s+)?meeting\b", re.I),
            ],
            "MEDIUM_HIGH": [
                re.compile(r"\b(?:first time meeting|nice to meet|just met)\b", re.I),
                re.compile(r"\bfollow[\s-]?up\s+(?:with|on|needed|required)\b", re.I),
                re.compile(r"\b(?:shipped|launched|deployed|published|released)\b", re.I),
                re.compile(r"\b(?:offer|accepted|rejected|approved|denied)\b", re.I),
                re.compile(r"\bintro(?:duce|duction)?\b", re.I),
            ],
            "MEDIUM": [
                re.compile(r"\b(?:new idea|insight|hypothesis|framework)\b", re.I),
                re.compile(r"\bresearch(?:ing|ed)?\s+\w+", re.I),
                re.compile(r"\b(?:reviewed|gave feedback|commented on)\b", re.I),
            ],
        }

    # ── Classification ───────────────────────────────────────────────

    def classify(
        self,
        event: dict[str, Any],
        context_events: list[dict[str, Any]] | None = None,
    ) -> ClassificationResult:
        buckets = [b for b in self._rubric.get("buckets", {}) if b != "other"]
        scores: dict[str, float] = {b: 0.0 for b in buckets}
        all_signals: list[SignalHit] = []
        layers_by_bucket: dict[str, set[str]] = {b: set() for b in buckets}

        searchable = self._build_searchable_text(event)
        app_name = (event.get("app") or "").casefold()
        entities = event.get("entities", {})
        people = entities.get("people", [])
        companies = entities.get("companies", [])
        urls = entities.get("urls", [])
        source_type = event.get("source_type", "desktop")

        for bucket_name in buckets:
            config = self._rubric["buckets"][bucket_name]
            signals = config.get("signals", {})

            # Layer 1: Source signal
            source_hits = self._score_source(app_name, source_type, signals, bucket_name)
            for hit in source_hits:
                scores[bucket_name] += hit.weight
                all_signals.append(hit)
                layers_by_bucket[bucket_name].add("source")

            # Layer 2: Entity signal
            entity_hits = self._score_entities(people, companies, bucket_name)
            for hit in entity_hits:
                scores[bucket_name] += hit.weight
                all_signals.append(hit)
                layers_by_bucket[bucket_name].add("entity")

            # Layer 3: Keyword signal
            kw_hits = self._score_keywords(searchable, signals, bucket_name)
            for hit in kw_hits:
                scores[bucket_name] += hit.weight
                all_signals.append(hit)
                if hit.weight > 0:
                    layers_by_bucket[bucket_name].add("keyword")

            # Layer 4: Domain signal
            domain_hits = self._score_domains(searchable, urls, signals, bucket_name)
            for hit in domain_hits:
                scores[bucket_name] += hit.weight
                all_signals.append(hit)
                layers_by_bucket[bucket_name].add("domain")

            # Layer 5: Context signal
            if context_events:
                context_hits = self._score_context(context_events, bucket_name)
                for hit in context_hits:
                    scores[bucket_name] += hit.weight
                    all_signals.append(hit)
                    layers_by_bucket[bucket_name].add("context")

        # Floor negative scores at 0
        for b in scores:
            if scores[b] < 0:
                scores[b] = 0.0

        # Apply keyword-only penalty
        for b in buckets:
            if scores[b] > 0 and layers_by_bucket[b] == {"keyword"}:
                original = scores[b]
                scores[b] *= self._keyword_only_penalty
                all_signals.append(SignalHit(
                    layer="penalty",
                    bucket=b,
                    detail=f"keyword-only penalty: {original:.1f} → {scores[b]:.1f}",
                    weight=scores[b] - original,
                ))

        # Sort buckets by score
        ranked = sorted(buckets, key=lambda b: scores[b], reverse=True)
        top_bucket = ranked[0]
        top_score = scores[top_bucket]
        second_bucket = ranked[1] if len(ranked) > 1 else "other"
        second_score = scores[second_bucket] if len(ranked) > 1 else 0.0

        # Determine uncertainty
        uncertain = False
        uncertainty_reason = ""
        candidate_buckets: list[str] = []

        if top_score < self._min_score:
            uncertain = True
            uncertainty_reason = f"top score ({top_score:.1f}) below threshold ({self._min_score})"
            candidate_buckets = [b for b in ranked if scores[b] > 0][:3]
        elif second_score > 0 and (second_score / top_score) >= self._ambiguity_ratio:
            uncertain = True
            uncertainty_reason = (
                f"ambiguous: {top_bucket}={top_score:.1f} vs {second_bucket}={second_score:.1f} "
                f"(ratio {second_score/top_score:.2f} >= {self._ambiguity_ratio})"
            )
            candidate_buckets = [top_bucket, second_bucket]

        # Calculate confidence
        if top_score == 0:
            confidence = 0.0
            final_bucket = "other"
        elif uncertain:
            confidence = min(0.3, top_score / 10.0)
            final_bucket = "uncertain"
        else:
            gap = (top_score - second_score) / top_score if top_score > 0 else 1.0
            confidence = min(1.0, gap * min(1.0, top_score / self._min_score))
            final_bucket = top_bucket

        # Determine priority
        priority = self._score_priority(searchable)

        # Collect all layers that fired for the winning bucket
        fired = layers_by_bucket.get(top_bucket, set()) if not uncertain else set()
        for b in candidate_buckets:
            fired |= layers_by_bucket.get(b, set())

        return ClassificationResult(
            bucket=final_bucket,
            confidence=round(confidence, 2),
            priority=priority,
            signals=all_signals,
            scores={b: round(s, 1) for b, s in scores.items() if s != 0},
            uncertain=uncertain,
            candidate_buckets=candidate_buckets,
            uncertainty_reason=uncertainty_reason,
            layers_fired=fired,
        )

    # ── Signal Layers ────────────────────────────────────────────────

    def _score_source(
        self, app_name: str, source_type: str, signals: dict, bucket: str
    ) -> list[SignalHit]:
        hits: list[SignalHit] = []
        if not app_name:
            return hits
        if app_name.strip("\u200e") in self._neutral_apps or app_name in self._neutral_apps:
            return hits
        source_cfg = signals.get("source", {})
        for app_entry in source_cfg.get("apps", []):
            entry_name = app_entry["name"].casefold()
            if entry_name in app_name or app_name in entry_name:
                hits.append(SignalHit(
                    layer="source",
                    bucket=bucket,
                    detail=f"app '{app_name}' matches '{app_entry['name']}'",
                    weight=app_entry.get("weight", 3),
                ))
        return hits

    def _score_entities(
        self, people: list[str], companies: list[str], bucket: str
    ) -> list[SignalHit]:
        def entity_text(value: Any) -> str:
            if isinstance(value, dict):
                return str(
                    value.get("name")
                    or value.get("full_name")
                    or value.get("email")
                    or value.get("domain")
                    or ""
                )
            return str(value or "")

        hits: list[SignalHit] = []
        for person in people:
            person_text = entity_text(person)
            key = person_text.casefold()
            if key in OWNER_NAMES:
                continue
            affiliations = self._entity_name_index.get(key, [])
            for parts in _name_parts_search(key):
                affiliations = affiliations or self._entity_name_index.get(parts, [])
            if bucket in affiliations:
                hits.append(SignalHit(
                    layer="entity",
                    bucket=bucket,
                    detail=f"person '{person_text}' affiliated with {bucket}",
                    weight=3,
                ))
        for company in companies:
            company_text = entity_text(company)
            key = company_text.casefold()
            affiliations = self._entity_company_index.get(key, [])
            if bucket in affiliations:
                hits.append(SignalHit(
                    layer="entity",
                    bucket=bucket,
                    detail=f"company '{company_text}' affiliated with {bucket}",
                    weight=3,
                ))
        return hits

    def _score_keywords(
        self, searchable: str, signals: dict, bucket: str
    ) -> list[SignalHit]:
        hits: list[SignalHit] = []
        kw_cfg = signals.get("keyword", {})
        for entry in kw_cfg.get("positive", []):
            term = entry["term"].casefold()
            if term in searchable:
                hits.append(SignalHit(
                    layer="keyword",
                    bucket=bucket,
                    detail=f"keyword '{entry['term']}'",
                    weight=entry.get("weight", 2),
                ))
        for entry in kw_cfg.get("negative", []):
            term = entry["term"].casefold()
            if term in searchable:
                hits.append(SignalHit(
                    layer="keyword",
                    bucket=bucket,
                    detail=f"negative keyword '{entry['term']}'",
                    weight=entry.get("weight", -2),
                ))
        return hits

    def _score_domains(
        self, searchable: str, urls: list[str], signals: dict, bucket: str
    ) -> list[SignalHit]:
        hits: list[SignalHit] = []
        domain_cfg = signals.get("domain", {})
        all_text = searchable + " " + " ".join(u.casefold() for u in urls)
        for entry in domain_cfg.get("positive", []):
            domain = entry["domain"].casefold()
            if domain in all_text:
                hits.append(SignalHit(
                    layer="domain",
                    bucket=bucket,
                    detail=f"domain '{entry['domain']}'",
                    weight=entry.get("weight", 3),
                ))
        for entry in domain_cfg.get("negative", []):
            domain = entry["domain"].casefold()
            if domain in all_text:
                hits.append(SignalHit(
                    layer="domain",
                    bucket=bucket,
                    detail=f"negative domain '{entry['domain']}'",
                    weight=entry.get("weight", -2),
                ))
        return hits

    def _score_context(
        self, context_events: list[dict[str, Any]], bucket: str
    ) -> list[SignalHit]:
        """Score based on adjacent events (temporal context window)."""
        hits: list[SignalHit] = []
        bucket_count = 0
        for ctx in context_events:
            ctx_bucket = ctx.get("_classified_bucket")
            if ctx_bucket == bucket and ctx.get("_classified_confidence", 0) > 0.5:
                bucket_count += 1
        if bucket_count >= 2:
            hits.append(SignalHit(
                layer="context",
                bucket=bucket,
                detail=f"{bucket_count} adjacent events in same bucket",
                weight=1.5,
            ))
        return hits

    # ── Priority ─────────────────────────────────────────────────────

    def _score_priority(self, searchable: str) -> str:
        for level in ("HIGH", "MEDIUM_HIGH", "MEDIUM"):
            for pat in self._priority_patterns.get(level, []):
                if pat.search(searchable):
                    return level
        return "LOW"

    # ── Helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _build_searchable_text(event: dict[str, Any]) -> str:
        def as_text(value: Any) -> str:
            if isinstance(value, dict):
                return str(
                    value.get("name")
                    or value.get("full_name")
                    or value.get("email")
                    or value.get("domain")
                    or ""
                )
            return str(value or "")

        parts = [
            as_text(event.get("title")),
            as_text(event.get("summary")),
        ]
        entities = event.get("entities", {})
        parts.extend(as_text(v) for v in entities.get("people", []))
        parts.extend(as_text(v) for v in entities.get("companies", []))
        parts.extend(as_text(v) for v in entities.get("urls", []))
        for action in event.get("actions", []):
            parts.append(as_text(action.get("object") if isinstance(action, dict) else action))
        return " ".join(parts).casefold()

    def classify_raw(
        self,
        raw_memory: dict[str, Any],
        context_events: list[dict[str, Any]] | None = None,
    ) -> tuple[dict[str, Any] | None, ClassificationResult | None]:
        """Classify a raw Sentience memory (activity_feed format)."""
        if raw_memory.get("source") == "Sentience Desktop App" or "source" not in raw_memory:
            event = self._raw_desktop_to_event(raw_memory)
        else:
            event = normalize(raw_memory)
        if event is None:
            return None, None
        result = self.classify(event, context_events)
        return event, result

    @staticmethod
    def _raw_desktop_to_event(raw: dict) -> dict[str, Any] | None:
        app = raw.get("app", "")
        if app == "Zo":
            return None
        event_id = raw.get("id", "")
        return {
            "event_id": event_id,
            "source_type": "desktop",
            "source_memory_id": event_id,
            "timestamp": raw.get("timestamp", ""),
            "app": app,
            "window_title": raw.get("window", ""),
            "title": raw.get("title", ""),
            "summary": raw.get("summary", ""),
            "category": raw.get("category"),
            "significance": raw.get("significance", 0.5),
            "entities": {
                "people": raw.get("people", []),
                "companies": raw.get("companies", []),
                "tools": raw.get("tools", []),
                "urls": raw.get("urls", []),
            },
            "actions": raw.get("actions", []),
            "sentiment": raw.get("sentiment"),
            "raw_content_hash": "",
        }

    def to_dict(self, result: ClassificationResult) -> dict:
        return {
            "bucket": result.bucket,
            "confidence": result.confidence,
            "priority": result.priority,
            "uncertain": result.uncertain,
            "candidate_buckets": result.candidate_buckets,
            "uncertainty_reason": result.uncertainty_reason,
            "scores": result.scores,
            "layers_fired": sorted(result.layers_fired),
            "signals": [
                {"layer": s.layer, "bucket": s.bucket, "detail": s.detail, "weight": s.weight}
                for s in result.signals
            ],
        }


def _name_parts_search(full_name: str) -> list[str]:
    """Generate partial name matches for fuzzy entity lookup."""
    parts = full_name.split()
    results = []
    if len(parts) >= 2:
        results.append(parts[0])
        results.append(parts[-1])
    return results


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Layered event classifier")
    parser.add_argument("--feed", type=str, help="Raw activity_feed.jsonl path")
    parser.add_argument("--normalized", type=str, help="Pre-normalized events JSONL path")
    parser.add_argument("--eval", type=str, help="Run eval against labeled examples JSONL")
    parser.add_argument("--verbose", action="store_true", help="Show signal breakdown")
    parser.add_argument("--limit", type=int, default=0, help="Max events to classify")
    parser.add_argument("--json", action="store_true", help="Output as JSON array")
    args = parser.parse_args()

    classifier = LayeredClassifier()

    if args.eval:
        _run_eval(classifier, Path(args.eval), args.verbose)
        return

    events = []
    if args.feed:
        path = Path(args.feed)
        raw_lines = path.read_text().strip().splitlines()
        for line in raw_lines:
            raw = json.loads(line)
            event, result = classifier.classify_raw(raw)
            if event and result:
                events.append((event, result))
            if args.limit and len(events) >= args.limit:
                break
    elif args.normalized:
        path = Path(args.normalized)
        for line in path.read_text().strip().splitlines():
            event = json.loads(line)
            result = classifier.classify(event)
            events.append((event, result))
            if args.limit and len(events) >= args.limit:
                break
    else:
        raw = json.load(sys.stdin)
        if "event_id" in raw:
            result = classifier.classify(raw)
            events.append((raw, result))
        else:
            event, result = classifier.classify_raw(raw)
            if event and result:
                events.append((event, result))

    if args.json:
        output = []
        for event, result in events:
            entry = {
                "event_id": event.get("event_id", event.get("id", "")),
                "title": event.get("title", ""),
                "app": event.get("app", ""),
                **classifier.to_dict(result),
            }
            output.append(entry)
        print(json.dumps(output, indent=2))
    else:
        from collections import Counter
        bucket_counts: Counter[str] = Counter()
        uncertain_count = 0
        for event, result in events:
            bucket_counts[result.bucket] += 1
            if result.uncertain:
                uncertain_count += 1
            if args.verbose:
                eid = event.get("event_id", event.get("id", "?"))
                app = event.get("app", "?")
                title = (event.get("title") or "")[:60]
                print(f"\n{'='*70}")
                print(f"  {eid} | {app} | {title}")
                print(f"  → {result.bucket} (conf={result.confidence}, pri={result.priority})")
                if result.uncertain:
                    print(f"  ⚠ UNCERTAIN: {result.uncertainty_reason}")
                    print(f"    candidates: {result.candidate_buckets}")
                print(f"  scores: {result.scores}")
                print(f"  layers: {sorted(result.layers_fired)}")
                if result.signals:
                    for s in result.signals:
                        sign = "+" if s.weight > 0 else ""
                        print(f"    [{s.layer}] {s.bucket}: {s.detail} ({sign}{s.weight})")

        print(f"\n{'='*70}")
        print(f"SUMMARY: {len(events)} events classified")
        for bucket, count in sorted(bucket_counts.items(), key=lambda x: -x[1]):
            print(f"  {bucket}: {count}")
        print(f"  (uncertain: {uncertain_count})")


def _run_eval(classifier: LayeredClassifier, eval_path: Path, verbose: bool):
    if not eval_path.exists():
        print(f"Eval file not found: {eval_path}", file=sys.stderr)
        sys.exit(1)
    lines = eval_path.read_text().strip().splitlines()
    total = 0
    correct = 0
    mismatches = []
    for line in lines:
        entry = json.loads(line)
        event = entry.get("event")
        expected_bucket = entry.get("correct_bucket")
        if not event or not expected_bucket:
            continue
        result = classifier.classify(event)
        total += 1
        predicted = result.bucket
        if predicted == expected_bucket:
            correct += 1
        else:
            mismatches.append({
                "event_id": event.get("event_id", "?"),
                "title": (event.get("title") or "")[:60],
                "expected": expected_bucket,
                "predicted": predicted,
                "confidence": result.confidence,
                "scores": result.scores,
            })
            if verbose:
                print(f"MISS: {event.get('event_id','?')}")
                print(f"  expected={expected_bucket} got={predicted}")
                print(f"  scores={result.scores}")
                for s in result.signals:
                    sign = "+" if s.weight > 0 else ""
                    print(f"  [{s.layer}] {s.bucket}: {s.detail} ({sign}{s.weight})")

    accuracy = correct / total if total > 0 else 0
    print(f"\nEVAL RESULTS: {correct}/{total} correct ({accuracy:.1%})")
    if mismatches:
        print(f"\nMISMATCHES ({len(mismatches)}):")
        for m in mismatches:
            print(f"  {m['event_id']}: expected={m['expected']} got={m['predicted']} (conf={m['confidence']})")


if __name__ == "__main__":
    main()
