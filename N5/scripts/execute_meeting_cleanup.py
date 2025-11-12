#!/usr/bin/env python3
"""
Execute meeting deduplication cleanup based on semantic LLM analysis.
Moves duplicate files to Trash with timestamp and logs all operations.
"""
import argparse
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)

# LLM-identified duplicates to delete (canonical versions are NOT in this list)
DUPLICATES_TO_DELETE = [
    # Acquisition War Room - 12 duplicates
    "Acquisition War Room-transcript-2025-11-03T19-48-05.399Z.transcript.md",
    "Acquisition_War_Room-transcript-2025-11-03T19-48-05.transcript.md",
    "Acquisition_War_Room-transcript-2025-11-03T19-50-56_686Z.transcript.md",
    "Acquisition_War_Room_2025-11-03T19-48-05.transcript.md",
    "Acquisition_War_Room_2025-11-03T19-50-56.transcript.md",
    "[IMPORTED-TO-ZO] Acquisition_War_Room-transcript-2025-11-03T19-48-05_399Z.transcript.md",
    "[IMPORTED-TO-ZO] Acquisition_War_Room-transcript-2025-11-03T19-50-56_686Z.transcript.md",
    "[IMPORTED-TO-ZO] Acquisition_War_Room_2025-11-03T19-50-56.transcript.md",
    
    # Daily team stand-up Oct 29 - 9 duplicates
    "Daily team stand-up-transcript-2025-10-29T14-37-53.274Z.transcript.md",
    "Daily_team_stand-up-transcript-2025-10-29T14-37-53_274Z.transcript.md",
    "Daily_team_stand-up-transcript-2025-10-29T14-38-58_996Z.transcript.md",
    "Daily_team_stand-up-transcript-2025-10-29T14-39-25_191Z.transcript.md",
    "Daily_team_stand-up_2025-10-29T14-38-58.transcript.md",
    "Daily_team_stand-up_2025-10-29T14-39-25.transcript.md",
    "[IMPORTED-TO-ZO] Daily_team_stand-up-transcript-2025-10-29T14-37-53_274Z.transcript.md",
    "[IMPORTED-TO-ZO] Daily_team_stand-up-transcript-2025-10-29T14-39-25_191Z.transcript.md",
    "[IMPORTED-TO-ZO] Daily_team_stand-up_2025-10-29T14-38-58.transcript.md",
    "[IMPORTED-TO-ZO] Daily_team_stand-up_2025-10-29T14-39-25.transcript.md",
    
    # Alex x Vrijen Wisdom Partners - 4 duplicates
    "Alex x Vrijen - Wisdom Partners Coaching-transcript-2025-10-29T17-58-28.439Z.transcript.md",
    "Alex_x_Vrijen_-_Wisdom_Partners_Coaching-transcript-2025-10-29T17-58-28.439Z.transcript.md",
    "Alex_x_Vrijen_Wisdom_Partners_Coaching-transcript-2025-10-29T17-58-28.439Z.transcript.md",
    "[IMPORTED-TO-ZO] Alex_x_Vrijen_Wisdom_Partners_Coaching-transcript-2025-10-29T17-58-28_439Z.transcript.md",
    
    # Careerspan Sam Partnership - 4 duplicates
    "Careerspan_Sam_Partnership_Discovery_Call-transcript-2025-10-24T17-32-41.785Z.transcript.md",
    "Careerspan_Sam_Partnership_Discovery_Call-transcript-2025-10-24T17-33-30.497Z.transcript.md",
    "Careerspan_Sam_Partnership_Discovery_Call-transcript-2025-10-24T17-34-52_747Z.transcript.md",
    "[IMPORTED-TO-ZO] Careerspan_Sam_Partnership_Discovery_Call-transcript-2025-10-24T17-34-52_747Z.transcript.md",
    
    # David x Careerspan - 5 duplicates (2 meetings)
    "David_x_Careerspan-transcript-2025-10-23T17-24-40.666Z.transcript.md",
    "[IMPORTED-TO-ZO] David_x_Careerspan-transcript-2025-10-23T17-24-40_666Z.transcript.md",
    "David x Careerspan-transcript-2025-10-27T17-10-48.436Z.transcript.md",
    "David_x_Careerspan-transcript-2025-10-27T17-10-48_436Z.transcript.md",
    "[IMPORTED-TO-ZO] David_x_Careerspan-transcript-2025-10-27T17-10-48_436Z.transcript.md",
    
    # Daily co-founder standup - 2 duplicates
    "Daily_co-founder_standup_check_trello-transcript-2025-10-31T13-33-29.723Z.transcript.md",
    "[IMPORTED-TO-ZO] Daily_co-founder_standup_check_trello-transcript-2025-10-31T13-33-29_723Z.transcript.md",
    
    # User Research Mujgan - 6 duplicates
    "User Research between Mujgan and Vrijen Attawar-transcript-2025-10-30T19-43-12.038Z.transcript.md",
    "User_Research_Mujgan_Vrijen_Attawar-transcript-2025-10-30T19-43-12-038Z.transcript.md",
    "User_Research_Mujgan_Vrijen_Attawar-transcript-2025-10-30T19-44-06-758Z.transcript.md",
    "User_Research_Mujgan_Vrijen_Attawar_2025-10-30T19-44-06.transcript.md",
    "User_Research_between_Mujgan_and_Vrijen_Attawar-transcript-2025-10-30T19-43-12.038Z.transcript.md",
    "User_Research_between_Mujgan_and_Vrijen_Attawar-transcript-2025-10-30T19-44-06_758Z.transcript.md",
    "[IMPORTED-TO-ZO] User_Research_between_Mujgan_and_Vrijen_Attawar-transcript-2025-10-30T19-44-06_758Z.transcript.md",
    
    # guz-dgac-fvk - 5 duplicates  
    "guz-dgac-fvk-transcript-2025-10-29T19-44-23.040Z.transcript.md",
    "guz-dgac-fvk-transcript-2025-10-29T19-45-58_924Z.transcript.md",
    "guz-dgac-fvk_2025-10-29T19-45-58.transcript.md",
    "[IMPORTED-TO-ZO] guz-dgac-fvk-transcript-2025-10-29T19-44-23_040Z.transcript.md",
    "[IMPORTED-TO-ZO] guz-dgac-fvk-transcript-2025-10-29T19-45-58_924Z.transcript.md",
    "[IMPORTED-TO-ZO] guz-dgac-fvk_2025-10-29T19-45-58.transcript.md",
    
    # dbn-ctum-szz - 4 duplicates
    "dbn-ctum-szz-transcript-2025-10-30T13-23-18.780Z.transcript.md",
    "dbn-ctum-szz-transcript-2025-10-30T13-24-03_256Z.transcript.md",
    "dbn-ctum-szz_2025-10-30T13-24-03.transcript.md",
    "[IMPORTED-TO-ZO] dbn-ctum-szz-transcript-2025-10-30T13-24-03_256Z.transcript.md",
    "[IMPORTED-TO-ZO] dbn-ctum-szz_2025-10-30T13-24-03.transcript.md",
    
    # Ilya meets the team - 1 duplicate
    "Ilya_meets_the_team-transcript-2025-11-04T15-40-19.transcript.md",
    
    # Remaining duplicates (grouped by meeting)
    "Gabi x Vrijen Zo Demo-transcript-2025-10-24T15-31-41.320Z.transcript.md",
    "Gabi_x_Vrijen_Zo_Demo-transcript-2025-10-24T15-31-41.320Z.transcript.md",
    "Gabi_x_Vrijen_Zo_Demo-transcript-2025-10-24T15-34-49.488Z.transcript.md",
    "[IMPORTED-TO-ZO] Gabi_x_Vrijen_Zo_Demo-transcript-2025-10-24T15-31-41_320Z.transcript.md",
]

def main(inbox_dir: str, dry_run: bool = True):
    """Execute cleanup based on LLM semantic analysis."""
    inbox_path = Path(inbox_dir).resolve()
    trash_dir = inbox_path.parent / "Trash"
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    trash_batch = trash_dir / f"DEDUP_CLEANUP_{timestamp}"
    
    if not inbox_path.exists():
        logging.error(f"Inbox not found: {inbox_path}")
        return 1
    
    trash_batch.mkdir(parents=True, exist_ok=True)
    log_file = trash_batch / "cleanup_log.jsonl"
    
    logging.info(f"{'DRY RUN: ' if dry_run else ''}Cleaning Inbox: {inbox_path}")
    logging.info(f"Trash destination: {trash_batch}")
    logging.info(f"Files to process: {len(DUPLICATES_TO_DELETE)}")
    
    moved = 0
    missing = 0
    errors = []
    
    for filename in DUPLICATES_TO_DELETE:
        source = inbox_path / filename
        dest = trash_batch / filename
        
        if not source.exists():
            logging.warning(f"Missing: {filename}")
            missing += 1
            continue
        
        try:
            if dry_run:
                logging.info(f"[DRY-RUN] Would move: {filename}")
            else:
                shutil.move(str(source), str(dest))
                log_entry = {
                    "filename": filename,
                    "moved_at": datetime.utcnow().isoformat() + "Z",
                    "source": str(source),
                    "dest": str(dest)
                }
                with log_file.open("a") as f:
                    f.write(json.dumps(log_entry) + "\n")
                logging.info(f"✓ Moved: {filename}")
            moved += 1
        except Exception as e:
            logging.error(f"Error moving {filename}: {e}")
            errors.append((filename, str(e)))
    
    logging.info("")
    logging.info(f"{'[DRY-RUN] ' if dry_run else ''}Summary:")
    logging.info(f"  Files processed: {moved}")
    logging.info(f"  Files missing: {missing}")
    logging.info(f"  Errors: {len(errors)}")
    
    if errors:
        logging.error("Errors encountered:")
        for filename, error in errors:
            logging.error(f"  {filename}: {error}")
    
    if not dry_run:
        logging.info(f"✓ Cleanup log: {log_file}")
    
    return 0 if len(errors) == 0 else 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Execute LLM-based meeting deduplication cleanup"
    )
    parser.add_argument("--inbox", default="/home/workspace/Personal/Meetings/Inbox",
                       help="Inbox directory path")
    parser.add_argument("--execute", action="store_true",
                       help="Execute cleanup (default is dry-run)")
    
    args = parser.parse_args()
    exit(main(args.inbox, dry_run=not args.execute))
