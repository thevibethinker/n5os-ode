#!/usr/bin/env python3
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

INBOX_DIR = Path("/home/workspace/Personal/Meetings/Inbox")

def validate_manifest(meeting_dir: Path) -> Tuple[bool, Dict]:
    """Check manifest.json for ready_for_state_transition status"""
    manifest_file = meeting_dir / "manifest.json"
    
    if not manifest_file.exists():
        return False, {"error": "manifest.json missing"}
    
    try:
        with open(manifest_file) as f:
            manifest = json.load(f)
        
        system_states = manifest.get("system_states", {})
        ready = system_states.get("ready_for_state_transition", {}).get("status", False)
        
        blocking_systems = []
        for system, state in system_states.items():
            if system != "ready_for_state_transition" and state.get("status") is False:
                blocking_systems.append(system)
        
        return ready, {
            "status": ready,
            "blocking_systems": blocking_systems,
            "raw": system_states
        }
    except json.JSONDecodeError:
        return False, {"error": "manifest.json malformed"}

def get_generated_blocks(meeting_dir: Path) -> List[str]:
    """Extract generated block names from manifest"""
    manifest_file = meeting_dir / "manifest.json"
    generated = []
    
    try:
        with open(manifest_file) as f:
            manifest = json.load(f)
        
        intelligence_blocks = manifest.get("intelligence_blocks", {})
        for block_name, block_info in intelligence_blocks.items():
            if block_info.get("status") == "generated":
                generated.append(block_name)
        
        return generated
    except:
        return []

def validate_files(meeting_dir: Path) -> Tuple[bool, Dict]:
    """Physically verify required files exist"""
    issues = []
    missing_files = []
    
    # Check for follow-up email
    follow_up = meeting_dir / "FOLLOW_UP_EMAIL.md"
    if not follow_up.exists():
        missing_files.append("FOLLOW_UP_EMAIL.md")
    
    # Check for warm intro
    warm_intro = meeting_dir / "B07_WARM_INTRO_BIDIRECTIONAL.md"
    if not warm_intro.exists():
        missing_files.append("B07_WARM_INTRO_BIDIRECTIONAL.md")
    
    # Check for generated intelligence blocks
    generated_blocks = get_generated_blocks(meeting_dir)
    for block_name in generated_blocks:
        block_file = meeting_dir / f"{block_name}_*.md"
        matching_files = list(meeting_dir.glob(f"{block_name}*.md"))
        if not matching_files:
            missing_files.append(f"{block_name}*.md")
    
    # Check B14 blurbs if present
    b14_file = meeting_dir / "B14_BLURBS_REQUESTED.jsonl"
    if b14_file.exists():
        try:
            with open(b14_file) as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        if entry.get("status") != "complete":
                            issues.append(f"B14 entry not complete: {entry.get('name', 'unknown')}")
                        
                        output_file = meeting_dir / "communications" / entry.get("output_file", "")
                        if not output_file.exists():
                            missing_files.append(f"communications/{entry.get('output_file')}")
        except Exception as e:
            issues.append(f"B14 file parsing error: {e}")
    
    is_valid = len(missing_files) == 0 and len(issues) == 0
    return is_valid, {
        "missing_files": missing_files,
        "issues": issues,
        "generated_blocks": generated_blocks
    }

def check_transition_readiness(meeting_dir: Path) -> Tuple[bool, Dict]:
    """Two-level validation: manifest + files"""
    manifest_ready, manifest_info = validate_manifest(meeting_dir)
    files_valid, file_info = validate_files(meeting_dir)
    
    # Trust files over manifest
    is_ready = files_valid or manifest_ready
    
    return is_ready, {
        "manifest": manifest_info,
        "files": file_info,
        "ready": is_ready,
        "trust_basis": "files" if files_valid else "manifest" if manifest_ready else "neither"
    }

def main():
    m_meetings = sorted([d for d in INBOX_DIR.iterdir() if d.is_dir() and d.name.endswith("[M]")])
    
    print(f"\n{'='*80}")
    print(f"STEP 1: SCAN [M] MEETINGS")
    print(f"{'='*80}\n")
    print(f"Found {len(m_meetings)} meeting(s) in [M] state\n")
    
    ready_to_transition = []
    still_blocked = []
    manifest_file_mismatches = []
    
    for meeting_dir in m_meetings:
        meeting_name = meeting_dir.name
        is_ready, validation_data = check_transition_readiness(meeting_dir)
        
        print(f"\n{'-'*80}")
        print(f"Meeting: {meeting_name}")
        print(f"{'-'*80}")
        
        manifest_status = validation_data["manifest"].get("status", False)
        files_status = len(validation_data["files"]["missing_files"]) == 0
        
        print(f"  Manifest Status: {'✓' if manifest_status else '✗'}")
        print(f"  Files Status: {'✓' if files_status else '✗'}")
        
        if manifest_status != files_status:
            mismatch_detail = {
                "name": meeting_name,
                "manifest_says": manifest_status,
                "files_show": files_status,
                "missing_files": validation_data["files"]["missing_files"],
                "blocking_systems": validation_data["manifest"].get("blocking_systems", [])
            }
            manifest_file_mismatches.append(mismatch_detail)
            print(f"  ⚠️  MISMATCH DETECTED (see details below)")
        
        if validation_data["files"]["missing_files"]:
            print(f"  Missing files:")
            for f in validation_data["files"]["missing_files"]:
                print(f"    - {f}")
        
        if validation_data["files"]["issues"]:
            print(f"  Issues:")
            for issue in validation_data["files"]["issues"]:
                print(f"    - {issue}")
        
        if validation_data["manifest"].get("blocking_systems"):
            print(f"  Blocking systems:")
            for sys in validation_data["manifest"]["blocking_systems"]:
                print(f"    - {sys}")
        
        if is_ready:
            print(f"  ✅ READY FOR TRANSITION")
            ready_to_transition.append(meeting_name)
        else:
            print(f"  ❌ BLOCKED - CANNOT TRANSITION")
            still_blocked.append({
                "name": meeting_name,
                "reason": validation_data["files"]["missing_files"] or validation_data["files"]["issues"] or validation_data["manifest"].get("blocking_systems", ["unknown"])
            })
    
    print(f"\n{'='*80}")
    print(f"STEP 2: TRANSITION RESULTS")
    print(f"{'='*80}\n")
    
    print(f"Total [M] meetings scanned: {len(m_meetings)}")
    print(f"Ready for transition: {len(ready_to_transition)}")
    print(f"Still blocked: {len(still_blocked)}")
    print(f"Manifest/file mismatches: {len(manifest_file_mismatches)}")
    
    if ready_to_transition:
        print(f"\n✅ READY FOR TRANSITION:")
        for name in ready_to_transition:
            print(f"  - {name}")
    
    if still_blocked:
        print(f"\n❌ BLOCKED (cannot transition):")
        for item in still_blocked:
            print(f"  - {item['name']}")
            for reason in item['reason'][:3]:  # Show first 3 reasons
                print(f"      • {reason}")
    
    if manifest_file_mismatches:
        print(f"\n⚠️  MANIFEST/FILE MISMATCHES:")
        for mismatch in manifest_file_mismatches:
            print(f"  - {mismatch['name']}")
            print(f"      Manifest: {mismatch['manifest_says']} | Files: {mismatch['files_show']}")
            if mismatch['missing_files']:
                print(f"      Missing: {', '.join(mismatch['missing_files'][:2])}")
    
    # Save results to JSON for step execution
    results = {
        "total_scanned": len(m_meetings),
        "ready_to_transition": ready_to_transition,
        "still_blocked": still_blocked,
        "manifest_file_mismatches": manifest_file_mismatches
    }
    
    results_file = Path("/home/.z/workspaces/con_ibX90dIy7iNBjREc/transition_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to {results_file}")
    return results

if __name__ == "__main__":
    main()

