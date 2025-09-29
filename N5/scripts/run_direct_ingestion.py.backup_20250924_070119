#!/usr/bin/env python3
"""
Command runner for direct-knowledge-ingest
Integrates with N5 command system
"""

import sys
import argparse
from pathlib import Path

# Add N5 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.direct_ingestion_mechanism import DirectKnowledgeIngestion

def main():
    parser = argparse.ArgumentParser(description="Run direct knowledge ingestion")
    parser.add_argument("--input_text", required=True, help="Text to ingest")
    parser.add_argument("--source_name", default="direct_ingestion", help="Source identifier")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")

    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN: Would process the following:")
        print(f"- Input length: {len(args.input_text)} characters")
        print(f"- Source: {args.source_name}")
        print("- Would create/update knowledge reservoirs:")
        print("  - bio.md (append)")
        print("  - timeline.md (append)")
        print("  - glossary.md (append)")
        print("  - sources.md (append)")
        print("  - facts.jsonl (append)")
        print("  - company/ files (overwrite)")
        return

    print("🚀 Starting direct knowledge ingestion...")
    print(f"📄 Processing {len(args.input_text)} characters from {args.source_name}")

    try:
        # Initialize direct processing
        ingestion = DirectKnowledgeIngestion()

        # Process the content
        structured_data = ingestion.process_large_document(args.input_text, args.source_name)

        # Save to reservoirs
        ingestion.save_to_reservoirs(structured_data)

        print("✅ Direct knowledge ingestion complete!")
        print(f"📁 Knowledge updated in: {ingestion.knowledge_dir}")

    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()