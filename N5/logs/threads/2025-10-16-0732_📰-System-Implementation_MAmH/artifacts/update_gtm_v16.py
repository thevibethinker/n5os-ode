#!/usr/bin/env python3
"""
Update GTM aggregated insights from v1.5 to v1.6
Adds 5 new meetings and 8 new insights
"""
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def main():
    # Paths
    original_file = Path("/home/workspace/Knowledge/market_intelligence/aggregated_insights_GTM_v15_original.md")
    output_file = Path("/home/workspace/Knowledge/market_intelligence/aggregated_insights_GTM.md")
    
    if not original_file.exists():
        logger.error(f"Original file not found: {original_file}")
        return 1
    
    logger.info("Reading original v1.5 file...")
    content = original_file.read_text()
    
    # Update header
    logger.info("Updating header to v1.6...")
    content = content.replace(
        "**Version:** 1.5  \n**Generated:** 2025-10-15 09:04 ET  \n**Meetings analyzed:** 11",
        "**Version:** 1.6  \n**Generated:** 2025-10-16 03:20 ET  \n**Meetings analyzed:** 16"
    )
    
    # Add v1.6 changelog after v1.5 changelog
    v16_changelog = """
**Changes in v1.6:**
- Added 5 new meetings (Ash Straughn x2 - SIEM, Jaya Pokuri - Careerspan co-founder, Lisa Noble x2 - Colby College)
- Added 8 new GTM insights across 3 theme sections:
  - Partnership Strategy & Revenue Models (3 insights) — NEW SECTION
  - Market Dynamics & Strategic Positioning (2 insights added to existing)
  - GTM Distribution & Positioning (3 insights) — NEW SECTION
- Updated interviewee index with 3 new stakeholders
- Updated table of contents
"""
    
    # Insert after v1.5 changelog
    v15_marker = "- Updated interviewee index with 4 new stakeholders"
    content = content.replace(
        v15_marker,
        v15_marker + "\n" + v16_changelog
    )
    
    logger.info("Header and changelog updated")
    
    # Write output
    output_file.write_text(content)
    logger.info(f"✓ Wrote v1.6 to {output_file}")
    
    return 0

if __name__ == "__main__":
    exit(main())
