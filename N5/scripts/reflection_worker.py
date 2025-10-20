#!/usr/bin/env python3
import argparse, json, logging, subprocess
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path("/home/workspace/N5/records/reflections")
INCOMING = ROOT / "incoming"
OUTPUTS = ROOT / "outputs"
REGISTRY = ROOT / "registry" / "registry.json"


def transcribe(audio_path: Path) -> Path:
    """Transcribe audio file or wrap text file. Handles both audio and text reflections.
    
    For audio files: Expects Zo's transcribe_audio tool was called before running this worker.
    For text files (.txt, .md): Auto-creates .transcript.jsonl wrapper if missing.
    """
    out = Path(str(audio_path) + ".transcript.jsonl")
    if out.exists():
        logger.info(f"✓ Transcript found: {out}")
        return out
    
    # Handle text files - create transcript wrapper automatically
    if audio_path.suffix.lower() in {'.txt', '.md'}:
        logger.info(f"Text file detected, creating transcript wrapper: {audio_path.name}")
        transcript_data = {
            "text": audio_path.read_text(),
            "source_file": str(audio_path),
            "mime_type": "text/plain"
        }
        out.write_text(json.dumps(transcript_data))
        logger.info(f"✓ Created transcript wrapper: {out.name}")
        return out
    
    # Handle audio files - require pre-transcription
    logger.error(f"Missing transcript: {out}")
    logger.error("Run: transcribe_audio tool on this file first, or call reflection_ingest which handles it automatically")
    raise FileNotFoundError(f"Transcript required: {out}")


def load_context(audio_path: Path) -> str:
    """Load email body context/instructions if available."""
    context_path = audio_path.parent / f"{audio_path.stem}_context.md"
    if context_path.exists():
        logger.info(f"Found context file: {context_path}")
        return context_path.read_text()
    return ""


def write_output(slug: str, name: str, content: str) -> Path:
    out_dir = OUTPUTS / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / name
    p.write_text(content)
    logger.info(f"Wrote: {p}")
    return p


def load_registry() -> dict:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    if REGISTRY.exists():
        return json.loads(REGISTRY.read_text())
    return {"items": []}


def save_registry(reg: dict):
    REGISTRY.write_text(json.dumps(reg, indent=2))


def update_registry(item: dict):
    reg = load_registry()
    reg["items"].append(item)
    save_registry(reg)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Absolute path to audio file in incoming/")
    args = parser.parse_args()

    audio = Path(args.file)
    assert audio.exists(), f"Missing audio: {audio}"

    slug = audio.stem
    transcript_path = transcribe(audio)
    context = load_context(audio)

    # Build context note if email body was provided
    context_note = f"\n\n## Context/Instructions\n{context}" if context else ""

    # Minimal summaries using existing pipeline script where possible
    summary_path = write_output(slug, "summary.md", f"# Summary\n\nSource: {audio.name}{context_note}\n\n(Generated summary placeholder — pipeline to replace)\n")
    detail_path = write_output(slug, "detail.md", f"# Detailed Recap\n\n(Generated recap placeholder — pipeline to replace)\n")

    # Proposal
    proposal_path = Path(f"/home/workspace/Records/Reflections/Proposals/{slug}_proposal.md")
    proposal_path.parent.mkdir(parents=True, exist_ok=True)
    proposal_path.write_text(f"# Proposal for {slug}\n\n- Option A: LinkedIn post\n- Option B: Newsletter snippet\n- Option C: Blog draft\n\nReply with your selections.\n")

    # Registry update
    item = {
        "id": slug,
        "source": str(audio),
        "ingested_at": datetime.now().isoformat(),
        "status": "awaiting-approval",
        "outputs": {
            "summary": str(summary_path),
            "detail": str(detail_path),
            "proposal": str(proposal_path)
        }
    }
    update_registry(item)

    logger.info("✓ Worker complete")

if __name__ == "__main__":
    main()
