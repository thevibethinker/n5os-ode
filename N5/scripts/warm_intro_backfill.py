#!/usr/bin/env python3
import argparse, logging, re
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MEETINGS_DIR = Path('/home/workspace/Personal/Meetings')

# Simple heuristics to detect potential intros
PATTERNS = {
    'outbound': re.compile(r"\b(I|I'll|I will|We|We will)\b.*\b(introduce|intro|connect)\b", re.I),
    'inbound': re.compile(r"\b(I can|I'll|I will|Happy to|Can)\b.*\b(introduce|intro|connect|share with my network|distribute)\b", re.I),
}

HEADER_OUTBOUND = "### Intros Vrijen Will Make (Outbound)\n\n"
HEADER_INBOUND = "### Intros Offered to Vrijen (Inbound)\n\n"


def read_text(p: Path) -> str:
    return p.read_text(encoding='utf-8', errors='ignore') if p.exists() else ''


def propose_b07(meeting_path: Path) -> str:
    b01 = read_text(meeting_path / 'B01_DETAILED_RECAP.md')
    b02 = read_text(meeting_path / 'B02_COMMITMENTS_CONTEXTUAL.md')
    b21 = read_text(meeting_path / 'B21_KEY_MOMENTS.md')
    text = "\n".join([b01, b02, b21])

    has_outbound = bool(PATTERNS['outbound'].search(text))
    has_inbound = bool(PATTERNS['inbound'].search(text))

    lines: List[str] = ["## WARM_INTRO_BIDIRECTIONAL", ""]

    if not has_outbound and not has_inbound:
        lines.append("No explicit warm introductions detected via backfill scan.")
        lines.append("")
        lines.append("**Note:** Backfill used heuristics over B01/B02/B21. If you recall specific intros, update this block manually.")
        return "\n".join(lines) + "\n"

    if has_outbound:
        lines.append(HEADER_OUTBOUND)
        lines.append("**TBD Contact → TBD Recipient**\n")
        lines.append("- **Who:** [Unknown] (backfilled)")
        lines.append("- **To Whom:** [Unknown] (backfilled)")
        lines.append("- **Why Relevant:** [To be filled]")
        lines.append("- **Context:** Extract from B01/B21")
        lines.append("- **Status:** Tentative - needs confirmation\n")

    if has_inbound:
        lines.append(HEADER_INBOUND)
        lines.append("**TBD Contact → Vrijen's Network**\n")
        lines.append("- **Who:** [Unknown] (backfilled)")
        lines.append("- **Available For:** [To be filled]")
        lines.append("- **Why It Matters:** [To be filled]")
        lines.append("- **Status:** Tentative - needs confirmation\n")

    return "\n".join(lines) + "\n"


def backfill(meeting_paths: List[Path], write: bool=False) -> List[Dict]:
    results = []
    for mp in meeting_paths:
        b07 = mp / 'B07_WARM_INTRO_BIDIRECTIONAL.md'
        status = 'skipped'
        note = ''
        existing = read_text(b07) if b07.exists() else ''
        needs_backfill = (not b07.exists()) or (existing.strip().startswith('## WARM_INTRO_BIDIRECTIONAL') and 'No explicit warm introductions' in existing)
        if needs_backfill:
            content = propose_b07(mp)
            if write:
                b07.write_text(content, encoding='utf-8')
                status = 'written'
            else:
                status = 'proposed'
                note = content.splitlines()[0:6]
        else:
            status = 'exists'
        results.append({'meeting': mp.name, 'status': status})
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=8)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    meetings = sorted([p for p in MEETINGS_DIR.iterdir() if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)[:args.limit]
    res = backfill(meetings, write=args.write)
    for r in res:
        logger.info(f"{r['meeting']}: {r['status']}")

if __name__ == '__main__':
    main()
