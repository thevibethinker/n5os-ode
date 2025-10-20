#!/usr/bin/env python3
"""
Reconstruct clean GTM v1.6 from available backups
Strategy: Use v1.3 (complete) as base, extract v1.5 content from backup, add v1.6 new sections
"""
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def main() -> int:
    try:
        # Read v1.3 (complete, 816 lines, has full structure)
        v13_file = Path("/home/workspace/Knowledge/market_intelligence/aggregated_insights_GTM_v1.3_backup_1760409230.md")
        v13_content = v13_file.read_text()
        logger.info(f"Read v1.3 base: {len(v13_content)} bytes")
        
        # Read v15 backup (has v1.5 content but incomplete)
        v15_file = Path("/home/workspace/Knowledge/market_intelligence/aggregated_insights_GTM_v15_backup.md")
        v15_content = v15_file.read_text()
        logger.info(f"Read v1.5 backup: {len(v15_content)} bytes")
        
        # Strategy: Find where v1.5 backup ends, extract the complete sections before that point
        # The v1.5 new sections are: Founder Pain Points, Recruiting Operations, Community Dynamics, Market Dynamics (expansion)
        
        # Extract from v1.5: everything from "## Founder Pain Points" through the end
        founder_start = v15_content.find("## Founder Pain Points & GTM Resourcing")
        if founder_start == -1:
            logger.error("Could not find Founder Pain Points section in v1.5")
            return 1
            
        v15_new_content = v15_content[founder_start:]
        logger.info(f"Extracted v1.5 new content: {len(v15_new_content)} bytes")
        
        # Now find where to insert this in v1.3 (after ## Monetization Models, before ## Synthesis)
        synthesis_marker = "## Synthesis"
        synthesis_pos = v13_content.find(synthesis_marker)
        if synthesis_pos == -1:
            logger.error("Could not find Synthesis section in v1.3")
            return 1
            
        # Insert v1.5 content before Synthesis
        base = v13_content[:synthesis_pos]
        ending = v13_content[synthesis_pos:]
        
        # Now read the v1.6 new sections from extraction document
        v16_extract = Path("/home/.z/workspaces/con_r33ooazGVs4kMAmH/gtm_v16_new_content.md")
        if not v16_extract.exists():
            logger.warning("v1.6 extraction document not found, will create placeholder")
            v16_sections = "\n\n## Partnership Strategy & Revenue Models\n\n[V1.6 CONTENT TO BE INSERTED]\n\n## GTM Distribution & Positioning\n\n[V1.6 CONTENT TO BE INSERTED]\n\n"
        else:
            v16_raw = v16_extract.read_text()
            # Extract the formatted sections (after "## Version Header Update")
            sections_start = v16_raw.find("## Partnership Strategy & Revenue Models")
            if sections_start > 0:
                # Find where new sections end (at "## Interviewee Index Updates")
                sections_end = v16_raw.find("## Interviewee Index Updates")
                if sections_end > 0:
                    v16_sections = "\n\n" + v16_raw[sections_start:sections_end].strip() + "\n\n"
                    logger.info(f"Extracted v1.6 sections: {len(v16_sections)} bytes")
                else:
                    v16_sections = "\n\n" + v16_raw[sections_start:].strip() + "\n\n"
            else:
                logger.warning("Could not parse v1.6 extraction, using empty")
                v16_sections = ""
        
        # Combine: v1.3 base + v1.5 content + v1.6 content + Synthesis + Interviewee Index
        reconstructed = base + v15_new_content + v16_sections + ending
        
        # Update header to v1.6
        reconstructed = reconstructed.replace(
            "**Version:** 1.3",
            "**Version:** 1.6"
        )
        reconstructed = reconstructed.replace(
            "**Meetings analyzed:** 7",
            "**Meetings analyzed:** 16"
        )
        
        # Update generated timestamp
        import re
        reconstructed = re.sub(
            r"\*\*Generated:\*\* [^\n]+",
            "**Generated:** 2025-10-16 03:30 ET",
            reconstructed
        )
        
        # Write output
        output_file = Path("/home/workspace/Knowledge/market_intelligence/aggregated_insights_GTM_v1.6_reconstructed.md")
        output_file.write_text(reconstructed)
        logger.info(f"✓ Wrote reconstructed v1.6: {len(reconstructed)} bytes to {output_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main())
