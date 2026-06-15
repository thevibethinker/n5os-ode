from __future__ import annotations

import json
import re
from pathlib import Path
from textwrap import dedent
from typing import Any, Optional

import yaml

WORKSPACE = Path("/home/workspace")
HYPOTHESIS_REGISTRY = WORKSPACE / "Personal" / "Knowledge" / "Frameworks" / "Hypotheses" / "registry.yaml"

PRIMARY_SHAPES = ["S01", "S02", "S03", "S04", "S05", "S06", "S07"]
CONDITIONAL_SHAPES = ["S08"]
POST_PROCESSORS = ["PP_GRAPH_EDGES"]

SHAPE_FILES = {
    "S01": "S01_CONTEXT.md",
    "S02": "S02_ACTIONS.md",
    "S03": "S03_EVIDENCE.md",
    "S04": "S04_PEOPLE.md",
    "S05": "S05_WISDOM.md",
    "S06": "S06_RECAP.md",
    "S07": "S07_ZO_DIRECTIVES.md",
    "S08": "S08_ZO_INTEL.md",
}

MACHINE_READABLE_SHAPE_FILES = {
    "S03": "S03_HYPOTHESIS_EVIDENCE.json",
}

POST_PROCESSOR_FILES = {
    "PP_GRAPH_EDGES": "PP_GRAPH_EDGES.jsonl",
}

LEGACY_BLOCK_TO_SHAPE = {
    "B00": "S07",
    "B01": "S06",
    "B02": "S02",
    "B02_B05": "S02",
    "B03": "S02",
    "B04": "S02",
    "B05": "S02",
    "B06": "S03",
    "B07": "S07",
    "B08": "S04",
    "B10": "S04",
    "B13": "S02",
    "B14": "S07",
    "B21": "S06",
    "B25": "S02",
    "B26": "S01",
    "B28": "S03",
    "B32": "S05",
    "B33": "S05",
    "B36": "S05",
    "B37": "S05",
    "B38": "S05",
    "B40": "S02",
    "B41": "S02",
    "B42": "S02",
    "B43": "S03",
    "B44": "S05",
    "B45": "S04",
    "B46": "S05",
    "B47": "S03",
    "B48": "S06",
    "B50": "S08",
    "B60": "S04",
}

LEGACY_FILE_CANDIDATES = {
    "B00": ["B00_ZO_TAKE_HEED.md"],
    "B01": ["B01_DETAILED_RECAP.md", "B01_detailed_recap.md"],
    "B02": ["B02_COMMITMENTS.md", "B02_commitments.md", "B02_DELIVERABLES_COMMITMENTS.md"],
    "B02_B05": ["B02_B05_COMMITMENTS_AND_ACTIONS.md"],
    "B03": ["B03_DECISIONS.md"],
    "B04": ["B04_OPEN_QUESTIONS.md"],
    "B05": ["B05_ACTION_ITEMS.md"],
    "B06": ["B06_BUSINESS_CONTEXT.md"],
    "B07": ["B07_WARM_INTRODUCTIONS.md"],
    "B08": ["B08_STAKEHOLDER_INTELLIGENCE.md", "B08_stakeholder_intelligence.md", "B08_FOLLOW_UP_CONVERSATIONS.md"],
    "B10": ["B10_RELATIONSHIP_TRAJECTORY.md"],
    "B13": ["B13_PLAN_OF_ACTION.md"],
    "B14": ["B14_BLURBS_REQUESTED.md"],
    "B21": ["B21_KEY_MOMENTS.md"],
    "B25": ["B25_DELIVERABLE_MAP.md", "B25_DELIVERABLE_CONTENT_MAP.md", "B25_deliverables.md"],
    "B26": ["B26_MEETING_METADATA.md", "B26_metadata.md", "B26_MEETING_TOPICS.md"],
    "B28": ["B28_STRATEGIC_INTELLIGENCE.md"],
    "B32": ["B32_THOUGHT_PROVOKING_IDEAS.md"],
    "B33": ["B33_DECISION_RATIONALE.md"],
    "B36": ["B36_STRATEGIC_MARKET_INSIGHTS.md"],
    "B37": ["B37_FRAMEWORKS_MENTAL_MODELS.md"],
    "B38": ["B38_NARRATIVE_FRAMES.md"],
    "B50": ["B50_ZO_TEAM_FEEDBACK.md"],
}

HOST_NAMES = {"v", "primary user", "host", "speaker 1"}
ZO_TERMS = [
    " zo ",
    "zo,",
    "zo.",
    "zocomputer",
    "zo computer",
    "zo.computer",
    "zo.space",
]
ZO_COMPETITOR_TERMS = ["cursor", "windsurf", "replit", "lovable", "bolt", "v0", "cline"]


def shape_filename(code: str) -> Optional[str]:
    return SHAPE_FILES.get(code) or POST_PROCESSOR_FILES.get(code)


def machine_readable_shape_filename(code: str) -> Optional[str]:
    return MACHINE_READABLE_SHAPE_FILES.get(code)


def artifact_stem(code: str) -> str:
    filename = shape_filename(code)
    if filename:
        return Path(filename).stem
    return code


def normalize_name(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def is_host_name(name: str) -> bool:
    return normalize_name(name).lower() in HOST_NAMES


def collect_participants(manifest: dict[str, Any]) -> list[dict[str, str]]:
    participants_raw = manifest.get("participants", [])
    participants: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add_item(name: Optional[str], email: Optional[str] = None, role: Optional[str] = None, org: Optional[str] = None) -> None:
        clean_name = normalize_name(name or "")
        clean_email = (email or "").strip().lower()
        if not clean_name and not clean_email:
            return
        key = (clean_name.lower(), clean_email)
        if key in seen:
            return
        seen.add(key)
        participants.append(
            {
                "name": clean_name or clean_email,
                "email": clean_email,
                "role": normalize_name(role or ""),
                "org": normalize_name(org or ""),
            }
        )

    if isinstance(participants_raw, dict):
        for bucket in ("identified", "unidentified"):
            for item in participants_raw.get(bucket, []):
                if isinstance(item, dict):
                    add_item(item.get("name"), item.get("email"), item.get("role"), item.get("company") or item.get("org"))
                elif isinstance(item, str):
                    add_item(item, item if "@" in item else None)
    elif isinstance(participants_raw, list):
        for item in participants_raw:
            if isinstance(item, dict):
                add_item(item.get("name"), item.get("email"), item.get("role"), item.get("company") or item.get("org"))
            elif isinstance(item, str):
                add_item(item, item if "@" in item else None)

    source = manifest.get("source", {})
    if isinstance(source, dict):
        for item in source.get("participants", []):
            if isinstance(item, dict):
                add_item(item.get("name"), item.get("email"), item.get("role"), item.get("company") or item.get("org"))
            elif isinstance(item, str):
                add_item(item, item if "@" in item else None)

    return participants


def infer_meeting_type(manifest: dict[str, Any]) -> str:
    nested_type = (manifest.get("meeting") or {}).get("type")
    if isinstance(nested_type, str) and nested_type.lower() in {"internal", "external"}:
        return nested_type.lower()
    crm_type = (manifest.get("crm_enrichment") or {}).get("classification")
    if isinstance(crm_type, str) and crm_type.lower() in {"internal", "external"}:
        return crm_type.lower()
    legacy_type = manifest.get("meeting_type")
    if isinstance(legacy_type, str) and legacy_type.lower() in {"internal", "external"}:
        return legacy_type.lower()
    return "external"


def _first_sentence(text: str, fallback: str) -> str:
    clean = re.sub(r"\s+", " ", text.strip())
    if not clean:
        return fallback
    for sentence in re.split(r"(?<=[.!?])\s+", clean):
        if len(sentence) >= 12:
            return sentence[:220]
    return clean[:220]


def build_context(meeting_path: Path, manifest: dict[str, Any], transcript: str) -> dict[str, Any]:
    meeting = manifest.get("meeting") or {}
    participants = collect_participants(manifest)
    source = manifest.get("source") or {}
    source_dict = source if isinstance(source, dict) else {}
    source_label_value = source if isinstance(source, str) else None

    summary = meeting.get("summary")
    summary_hint = ""
    if isinstance(summary, dict):
        summary_hint = summary.get("overview") or summary.get("shorthand_bullet") or ""
    elif isinstance(summary, str):
        summary_hint = summary

    title = (
        meeting.get("title")
        or manifest.get("title")
        or meeting.get("name")
        or meeting_path.name.replace("_", " ")
    )
    date = meeting.get("date") or manifest.get("date") or manifest.get("meeting_date") or "Unknown"
    duration = (
        meeting.get("duration_minutes")
        or manifest.get("duration_minutes")
        or manifest.get("duration")
        or "Unknown"
    )
    source_label = source_dict.get("type") or source_dict.get("format") or source_dict.get("adapter") or source_label_value or "Unknown"
    org = (
        (manifest.get("org_classification") or {}).get("org")
        or (manifest.get("org_classification") or {}).get("canonical_org")
        or manifest.get("org")
        or meeting.get("org")
        or "Unknown"
    )
    purpose = (
        meeting.get("purpose")
        or manifest.get("purpose")
        or manifest.get("summary")
        or _first_sentence(summary_hint, "")
        or _first_sentence(transcript[:800], title)
    )

    return {
        "meeting_id": manifest.get("meeting_id") or meeting_path.name,
        "title": title,
        "date": str(date),
        "duration": str(duration),
        "meeting_type": infer_meeting_type(manifest),
        "org": str(org),
        "source": str(source_label),
        "purpose": str(purpose),
        "participants": participants,
    }


def render_context_markdown(context: dict[str, Any]) -> str:
    participants_summary = "; ".join(
        [
            part["name"]
            + (
                f" ({', '.join([token for token in [part.get('role'), part.get('org')] if token])})"
                if part.get("role") or part.get("org")
                else ""
            )
            for part in context.get("participants", [])
        ]
    ) or "Unknown"

    lines = [
        "# CONTEXT",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| **Date** | {context.get('date', 'Unknown')} |",
        f"| **Duration** | {context.get('duration', 'Unknown')} |",
        f"| **Type** | {context.get('meeting_type', 'Unknown')} |",
        f"| **Org** | {context.get('org', 'Unknown')} |",
        f"| **Participants** | {participants_summary} |",
        f"| **Purpose** | {context.get('purpose', 'Unknown')} |",
        f"| **Source** | {context.get('source', 'Unknown')} |",
        "",
        "## Participant Details",
        "",
    ]

    if not context.get("participants"):
        lines.append("No participant details available.")
        return "\n".join(lines).strip() + "\n"

    for participant in context["participants"]:
        lines.extend(
            [
                f"### {participant.get('name') or 'Unknown'}",
                f"- **Role:** {participant.get('role') or 'Unknown'}",
                f"- **Org:** {participant.get('org') or 'Unknown'}",
                f"- **Email:** {participant.get('email') or 'Unknown'}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def load_active_hypotheses(limit: Optional[int] = None) -> list[dict[str, Any]]:
    if not HYPOTHESIS_REGISTRY.exists():
        return []
    data = yaml.safe_load(HYPOTHESIS_REGISTRY.read_text()) or {}
    hypotheses = [item for item in data.get("hypotheses", []) if item.get("active")]
    if limit is not None:
        return hypotheses[:limit]
    return hypotheses


def hypotheses_prompt_context(limit: int = 40) -> str:
    items = load_active_hypotheses(limit=limit)
    if not items:
        return "- No active hypotheses registry found."
    return "\n".join(f"- {item['id']}: {item['statement']}" for item in items)


def should_generate_zo_intel(transcript: str, context: dict[str, Any]) -> tuple[bool, str]:
    if context.get("meeting_type") == "internal":
        return False, "internal_meeting"

    lowered = f" {transcript.lower()} "
    if not any(term in lowered for term in ZO_TERMS):
        return False, "zo_not_mentioned"

    non_host_zo_mentions = 0
    for line in transcript.splitlines():
        if ":" not in line:
            continue
        speaker, utterance = line.split(":", 1)
        if is_host_name(speaker):
            continue
        utterance_lower = f" {utterance.lower()} "
        if any(term in utterance_lower for term in ZO_TERMS) or any(term in utterance_lower for term in ZO_COMPETITOR_TERMS):
            non_host_zo_mentions += 1

    if non_host_zo_mentions == 0:
        return False, "zo_only_from_host"
    return True, f"external_non_host_zo_mentions={non_host_zo_mentions}"


def determine_shape_plan(transcript: str, context: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    shapes = PRIMARY_SHAPES.copy()
    zo_triggered, zo_reason = should_generate_zo_intel(transcript, context)
    if zo_triggered:
        shapes.append("S08")
    selection = {
        "method": "shape_router_v1",
        "always": PRIMARY_SHAPES.copy(),
        "conditional_selected": ["S08"] if zo_triggered else [],
        "conditional_skipped": [] if zo_triggered else ["S08"],
        "reasoning": {"S08": zo_reason},
        "post_processors": POST_PROCESSORS.copy(),
    }
    return shapes + POST_PROCESSORS, selection


def truncate_transcript(transcript: str, max_chars: int = 30000) -> str:
    if len(transcript) <= max_chars:
        return transcript
    return transcript[:max_chars] + "\n\n[... transcript truncated for token limit ...]"


def sanitize_model_output(text: str) -> str:
    clean = text.strip()
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    clean = re.sub(r"\n\*?\d{2}/\d{2}/\d{4} \d{1,2}:\d{2} [AP]M ET\*?\s*$", "", clean, flags=re.I)
    clean = re.sub(r"\n\*?\d{4}-\d{2}-\d{2} \d{1,2}:\d{2} [AP]M ET\*?\s*$", "", clean, flags=re.I)
    clean = re.sub(r"\n\*?2026-\d{2}-\d{2} .*?ET\*?\s*$", "", clean, flags=re.I)
    return clean.strip() + "\n"


def sanitize_json_output(text: str) -> Any:
    clean = text.strip()
    if clean.startswith("```"):
        lines = clean.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        clean = "\n".join(lines).strip()
    return json.loads(clean)


def _participant_line(context: dict[str, Any]) -> str:
    return ", ".join(part["name"] for part in context.get("participants", []) if part.get("name")) or "Unknown"


def build_shape_prompt(shape_code: str, transcript: str, context: dict[str, Any], meeting_path: Path) -> str:
    max_chars = 30000
    if shape_code == "S06":
        max_chars = 12000
    elif shape_code == "S04":
        max_chars = 18000
    elif shape_code == "S07":
        max_chars = 16000
    transcript_excerpt = truncate_transcript(transcript, max_chars=max_chars)
    shared_context = dedent(
        f"""
        ## Meeting Context
        - Meeting ID: {context.get('meeting_id', meeting_path.name)}
        - Title: {context.get('title', meeting_path.name)}
        - Date: {context.get('date', 'Unknown')}
        - Type: {context.get('meeting_type', 'external')}
        - Org: {context.get('org', 'Unknown')}
        - Participants: {_participant_line(context)}
        - Purpose: {context.get('purpose', 'Unknown')}
        - Source: {context.get('source', 'Unknown')}

        ## Transcript
        {transcript_excerpt}
        """
    ).strip()

    if shape_code == "S02":
        return dedent(
            f"""
            You are generating the ACTIONS shape for a meeting intelligence system.
            Optimize in this order: actionability, specificity, truthful extraction, readability.

            {shared_context}

            Output markdown starting with `# ACTIONS`.

            Required structure:
            # ACTIONS
            ## Decisions
            ## Commitments & Tasks
            ## Open Items

            Rules:
            - Every task must have an owner, a concrete first step, and deadline if stated.
            - Keep decisions separate from tasks.
            - Open items are unresolved questions or blockers only.
            - If a section has nothing, say so plainly.
            - No invented deadlines, no invented owners.
            """
        ).strip()

    if shape_code == "S03":
        return dedent(
            f"""
            You are generating the EVIDENCE shape for a meeting intelligence system.
            Extract only hypothesis-relevant evidence. Do not turn general insights into evidence if they do not map cleanly.

            ## Active Hypotheses
            {hypotheses_prompt_context()}

            {shared_context}

            Output markdown starting with `# EVIDENCE`.

            Rules:
            - Maximum 5 evidence items.
            - Every item needs: Hypothesis, Direction, Signal strength, Quote, Speaker, Context, Why it matters.
            - Use exact transcript quotes.
            - If nothing clearly maps, output `# EVIDENCE` followed by `No evidence items identified.`
            - At most 1 UNTAGGED item if truly important.
            """
        ).strip()

    if shape_code == "S04":
        return dedent(
            f"""
            You are generating the PEOPLE shape for a meeting intelligence system.
            Extract participant-level intelligence from THIS meeting only.

            {shared_context}

            Output markdown starting with `# PEOPLE`.

            For each non-host participant, include:
            - Profile
            - What They Care About
            - Standout quote
            - What Resonated
            - Domain authority
            - Relationship signal
            - Next-touch recommendation

            Rules:
            - Only claim domain authority where firsthand knowledge appeared in the transcript.
            - Keep V context minimal unless needed for relationship signal.
            - No CRM commands, no speculative web research, no external enrichment.
            """
        ).strip()

    if shape_code == "S05":
        return dedent(
            f"""
            You are generating the WISDOM shape for a meeting intelligence system.
            Capture only durable, reusable material worth memory promotion.

            {shared_context}

            Output markdown starting with `# WISDOM`.

            Each item must include:
            - Type: belief / strategy / framework / narrative / decision-rationale / external-wisdom
            - Content
            - Why it matters
            - Reuse potential
            - Evidence quote

            Rules:
            - High bar. Skip generic observations and tactical meeting chatter.
            - Keep to at most 6 items.
            - If nothing qualifies, output `# WISDOM` followed by `No durable wisdom items identified.`
            """
        ).strip()

    if shape_code == "S06":
        return dedent(
            f"""
            You are generating the RECAP shape for a meeting intelligence system.
            This is the human skim artifact: concise, chronological, specific.

            {shared_context}

            Output markdown starting with `# RECAP`.

            Required structure:
            - Overview
            - What Happened
            - Key Quotes
            - Takeaways

            Rules:
            - 3-5 paragraphs in the narrative portion.
            - Use real names, decisions, numbers, and turning points.
            - 2-4 quotes maximum, each adding distinct signal.
            - No transcript-style speaker logs.
            """
        ).strip()

    if shape_code == "S07":
        return dedent(
            f"""
            You are generating the ZO_DIRECTIVES shape for a meeting intelligence system.
            Detect only instructions directed at Zo by V.

            {shared_context}

            Output markdown starting with `# ZO_DIRECTIVES`.

            Required structure:
            - Summary line with Detected and Rejected counts
            - One fenced jsonl block containing zero or more directive records
            - Optional Notes section

            Rules:
            - ONLY V can trigger directives.
            - Detect warm intro, blurb, follow-up, research, crm_contact, deal_add, deal_update, list_add, intro_lead, directive, custom.
            - Use execution_policy `inline` for directive and `auto_execute` for the rest unless the transcript clearly says otherwise.
            - If there are none, still output an empty jsonl block and note `No Zo directives detected.`
            """
        ).strip()

    if shape_code == "S08":
        return dedent(
            f"""
            You are generating the ZO_INTEL shape for a meeting intelligence system.
            Extract Zo-relevant competitive, strategic, market, and product intel from EXTERNAL voices only.

            {shared_context}

            Output markdown starting with `# ZO_INTEL`.

            Rules:
            - External voices only. V explaining or praising Zo is context, not intel.
            - Keep total output between 40 and 60 lines.
            - Include Key Intel, Notable Quotes, Intelligence Breakdown, Actionable Takeaways, Signal Summary.
            - Be honest about negative or critical feedback.
            - If the meeting does not contain substantive external Zo intel, return exactly:
              `# ZO_INTEL`
              `No substantive external Zo intelligence identified.`
            """
        ).strip()

    raise ValueError(f"Unknown shape code: {shape_code}")


def build_evidence_json_prompt(transcript: str, context: dict[str, Any], meeting_path: Path) -> str:
    transcript_excerpt = truncate_transcript(transcript, max_chars=24000)
    meeting_id = context.get('meeting_id', meeting_path.name)
    observed_at = context.get('date', 'Unknown')
    participants = _participant_line(context)
    hypotheses = hypotheses_prompt_context()
    return dedent(
        f"""
        Convert this meeting into a machine-readable hypothesis evidence artifact.
        Output ONLY valid JSON. No markdown. No code fences.

        Required top-level shape:
        {{
          "meeting_id": "{meeting_id}",
          "captured_from_shape": "hypothesis_evidence",
          "observed_at": "{observed_at}",
          "items": [
            {{
              "hypothesis_id": "H-... or UNTAGGED",
              "direction": "supports|weakens|mixed|neutral",
              "confidence": "low|medium|high",
              "strength": "low|medium|high",
              "claim": "normalized claim in your own words",
              "summary": "1-2 sentence explanation of why this is evidence",
              "speaker": "speaker name or Unknown",
              "speaker_scope": "partner|external_buyer|investor|internal_team|mixed|unknown",
              "quote": "direct quote from transcript",
              "context": "brief meeting context for this evidence",
              "why_it_matters": "why this should update belief",
              "source_excerpt_ids": ["EX-001"],
              "source_excerpts": [{{"id": "EX-001", "speaker": "Name", "text": "quote text"}}],
              "source_block_id": "S03_EVIDENCE",
              "source_type": "meeting"
            }}
          ]
        }}

        Rules:
        - Maximum 5 items.
        - Use only hypotheses from the active registry below. If nothing maps cleanly, return an empty items array.
        - `captured_from_shape` must be exactly `hypothesis_evidence`.
        - Every item must include direct quote evidence and source excerpt IDs.
        - `claim` must be normalized, not just a raw quote.
        - If the signal is important but not registry-mapped, use `UNTAGGED` as hypothesis_id.
        - If no evidence exists, still return the top-level object with an empty `items` array.

        Active hypotheses:
        {hypotheses}

        Meeting context:
        - Meeting ID: {meeting_id}
        - Date: {observed_at}
        - Type: {context.get('meeting_type', 'external')}
        - Org: {context.get('org', 'Unknown')}
        - Participants: {participants}
        - Purpose: {context.get('purpose', 'Unknown')}

        Transcript:
        {transcript_excerpt}
        """
    ).strip()


def build_graph_edges_prompt(meeting_path: Path, context: dict[str, Any], shape_bundle: dict[str, str]) -> str:
    ordered = []
    for code in PRIMARY_SHAPES + CONDITIONAL_SHAPES:
        if code in shape_bundle and shape_bundle[code]:
            ordered.append(f"## {code}\n{shape_bundle[code]}")
    bundle_text = "\n\n".join(ordered)[:40000]
    return dedent(
        f"""
        You are generating context graph edges from meeting intelligence shapes.

        ## Meeting
        - Meeting ID: {context.get('meeting_id', meeting_path.name)}
        - Title: {context.get('title', meeting_path.name)}
        - Date: {context.get('date', 'Unknown')}
        - Participants: {_participant_line(context)}

        ## Shapes
        {bundle_text}

        Output ONLY JSONL.
        First line must be a metadata object:
        {{"_meta": true, "meeting_id": "{context.get('meeting_id', meeting_path.name)}", "generated_at": "ISO8601", "shapes_read": ["S01","S02","S03","S04","S05","S06","S07"]}}

        Then emit 3-8 edge objects with keys:
        source_type, source_id, relation, target_type, target_id, evidence, context_meeting_id

        Allowed relations:
        originated_by, supported_by, challenged_by, hoped_for, concerned_about,
        influenced_by, depends_on, supports_position, challenges_position,
        crystallized_from, evolves

        Rules:
        - Use evidence from the shapes, not the raw transcript.
        - Only emit high-signal edges.
        - Every edge must include evidence.
        - If there are fewer than 3 strong edges, emit only the strong ones. Do not pad.
        """
    ).strip()


def find_artifact_path(meeting_path: Path, key: str) -> Optional[Path]:
    normalized = key.strip().upper()
    filename = shape_filename(normalized)
    if filename:
        path = meeting_path / filename
        if path.exists():
            return path

    preferred_shape = LEGACY_BLOCK_TO_SHAPE.get(normalized)
    if preferred_shape:
        preferred_filename = shape_filename(preferred_shape)
        if preferred_filename:
            preferred_path = meeting_path / preferred_filename
            if preferred_path.exists():
                return preferred_path

    for candidate in LEGACY_FILE_CANDIDATES.get(normalized, []):
        path = meeting_path / candidate
        if path.exists():
            return path

    if normalized.startswith("B"):
        matches = sorted(meeting_path.glob(f"{normalized}*.md"))
        if matches:
            return matches[0]
    return None


def read_artifact_text(meeting_path: Path, key: str) -> Optional[str]:
    path = find_artifact_path(meeting_path, key)
    if not path or not path.exists():
        return None
    text = path.read_text().strip()
    return text or None


def resolve_requested_texts(meeting_path: Path, keys: list[str]) -> dict[str, str]:
    resolved: dict[str, str] = {}
    for key in keys:
        text = read_artifact_text(meeting_path, key)
        if text:
            resolved[key] = text
    return resolved


def read_shape_bundle(meeting_path: Path) -> dict[str, str]:
    bundle: dict[str, str] = {}
    for code, filename in SHAPE_FILES.items():
        path = meeting_path / filename
        if path.exists():
            bundle[code] = path.read_text()
    return bundle
