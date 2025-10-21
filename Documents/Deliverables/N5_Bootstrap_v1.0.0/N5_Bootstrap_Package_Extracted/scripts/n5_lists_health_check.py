#!/usr/bin/env python3
"""
N5 Lists Health Check with Phase 3 Trigger Detection

Monitors list system health and detects conditions that warrant Phase 3 implementation:
- List count exceeds threshold (>20 total lists)
- High similarity between lists (merge opportunities)
- Frequent manual merge considerations
- Maintenance burden indicators

Outputs:
- Health status report
- Phase 3 trigger alerts
- Recommendations for next actions
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
LISTS_DIR = ROOT / "lists"
INDEX_FILE = LISTS_DIR / "index.jsonl"
SYSTEM_UPGRADES = LISTS_DIR / "system-upgrades.jsonl"

# Phase 3 Trigger Thresholds
THRESHOLDS = {
    "list_count_warning": 15,      # Start paying attention
    "list_count_critical": 20,     # Phase 3.1 recommended
    "list_count_urgent": 30,       # Phase 3 strongly recommended
    "similar_list_threshold": 0.6  # 60% title/tag overlap suggests merge opportunity
}

def read_jsonl(p: Path):
    """Read JSONL file and return list of items."""
    items = []
    if not p.exists():
        return items
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            ln = line.strip()
            if ln:
                try:
                    items.append(json.loads(ln))
                except json.JSONDecodeError:
                    continue
    return items

def get_list_count():
    """Count registered lists in index."""
    registry = read_jsonl(INDEX_FILE)
    return len(registry)

def get_all_lists():
    """Get all list metadata from registry."""
    return read_jsonl(INDEX_FILE)

def calculate_similarity(list1, list2):
    """
    Calculate simple similarity score between two lists based on:
    - Title keyword overlap
    - Tag overlap
    - Description similarity
    """
    title1 = set(list1.get("title", "").lower().split())
    title2 = set(list2.get("title", "").lower().split())
    
    tags1 = set(list1.get("tags", []))
    tags2 = set(list2.get("tags", []))
    
    # Remove common words
    stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
    title1 = title1 - stopwords
    title2 = title2 - stopwords
    
    if not title1 or not title2:
        return 0.0
    
    title_overlap = len(title1 & title2) / max(len(title1), len(title2))
    tag_overlap = len(tags1 & tags2) / max(len(tags1), len(tags2)) if (tags1 or tags2) else 0
    
    # Weighted average: titles matter more
    similarity = (title_overlap * 0.7) + (tag_overlap * 0.3)
    return similarity

def detect_similar_lists(lists):
    """Detect pairs of lists with high similarity."""
    similar_pairs = []
    
    for i, list1 in enumerate(lists):
        for list2 in lists[i+1:]:
            similarity = calculate_similarity(list1, list2)
            if similarity >= THRESHOLDS["similar_list_threshold"]:
                similar_pairs.append({
                    "list1": list1.get("slug", "unknown"),
                    "list2": list2.get("slug", "unknown"),
                    "similarity": round(similarity, 2),
                    "reason": f"{int(similarity * 100)}% overlap in titles/tags"
                })
    
    return similar_pairs

def check_phase3_triggers():
    """Check if any Phase 3 trigger conditions are met."""
    triggers = {
        "list_count_status": "ok",
        "list_count": 0,
        "similar_lists": [],
        "phase3_recommended": False,
        "urgency": "none",  # none, low, medium, high
        "recommendations": []
    }
    
    # Check list count
    list_count = get_list_count()
    triggers["list_count"] = list_count
    
    if list_count >= THRESHOLDS["list_count_urgent"]:
        triggers["list_count_status"] = "urgent"
        triggers["urgency"] = "high"
        triggers["phase3_recommended"] = True
        triggers["recommendations"].append(
            f"⚠️ URGENT: {list_count} lists detected (threshold: {THRESHOLDS['list_count_urgent']}). "
            "Phase 3 implementation strongly recommended."
        )
    elif list_count >= THRESHOLDS["list_count_critical"]:
        triggers["list_count_status"] = "critical"
        triggers["urgency"] = "medium"
        triggers["phase3_recommended"] = True
        triggers["recommendations"].append(
            f"⚠️ WARNING: {list_count} lists detected (threshold: {THRESHOLDS['list_count_critical']}). "
            "Consider implementing Phase 3.1 (Similarity Scanner)."
        )
    elif list_count >= THRESHOLDS["list_count_warning"]:
        triggers["list_count_status"] = "warning"
        triggers["urgency"] = "low"
        triggers["recommendations"].append(
            f"ℹ️ INFO: {list_count} lists detected (threshold: {THRESHOLDS['list_count_warning']}). "
            "Approaching Phase 3 threshold. Monitor list growth."
        )
    else:
        triggers["recommendations"].append(
            f"✅ List count healthy: {list_count} lists (Phase 3 threshold: {THRESHOLDS['list_count_critical']})"
        )
    
    # Check for similar lists
    all_lists = get_all_lists()
    similar_lists = detect_similar_lists(all_lists)
    triggers["similar_lists"] = similar_lists
    
    if similar_lists:
        triggers["phase3_recommended"] = True
        if triggers["urgency"] == "none":
            triggers["urgency"] = "low"
        
        triggers["recommendations"].append(
            f"⚠️ MERGE OPPORTUNITY: {len(similar_lists)} pairs of similar lists detected. "
            "Consider manual merge or implement Phase 3.2 (List Merger)."
        )
        
        for pair in similar_lists[:3]:  # Show top 3
            triggers["recommendations"].append(
                f"   - '{pair['list1']}' ↔ '{pair['list2']}' ({pair['reason']})"
            )
    
    return triggers

def create_phase3_alert():
    """Create a system upgrade alert for Phase 3 implementation."""
    alert = {
        "id": f"phase3-lists-trigger-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        "title": "Phase 3 List System Implementation Recommended",
        "summary": "List system health check detected conditions warranting Phase 3 implementation",
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "priority": "M",
        "tags": ["lists", "phase3", "automation", "maintenance"],
        "body": (
            "The list system health check has detected trigger conditions for Phase 3 implementation. "
            "Review the list system status report and consider implementing:\n\n"
            "Phase 3.1: List Similarity Detection\n"
            "Phase 3.2: Semi-Automated List Merging\n"
            "Phase 3.3: Enhanced Auto-Correction\n\n"
            "Reference: N5 Lists System Improvement Plan (con_iCXGjocGU0NRU0B3/n5_lists_improvement_plan.md)\n"
            "Status Report: con_pQh91lSEsCkaqLRz/list_system_implementation_status.md"
        )
    }
    return alert

def add_system_upgrade(alert):
    """Add Phase 3 alert to system-upgrades list."""
    # Check if alert already exists
    existing = read_jsonl(SYSTEM_UPGRADES)
    for item in existing:
        if item.get("id", "").startswith("phase3-lists-trigger-"):
            # Alert already exists, don't duplicate
            return False
    
    # Add new alert
    with SYSTEM_UPGRADES.open("a", encoding="utf-8") as f:
        f.write(json.dumps(alert) + "\n")
    
    return True

def main():
    """Run health check and detect Phase 3 triggers."""
    print("=" * 70)
    print("N5 Lists System Health Check")
    print("=" * 70)
    print()
    
    triggers = check_phase3_triggers()
    
    # Display status
    print(f"📊 Current Status:")
    print(f"   List Count: {triggers['list_count']}")
    print(f"   Status: {triggers['list_count_status'].upper()}")
    print(f"   Urgency: {triggers['urgency'].upper()}")
    print(f"   Phase 3 Recommended: {'YES' if triggers['phase3_recommended'] else 'NO'}")
    print()
    
    # Display recommendations
    print("📋 Recommendations:")
    for rec in triggers["recommendations"]:
        print(f"   {rec}")
    print()
    
    # If similar lists detected, show details
    if triggers["similar_lists"]:
        print("🔍 Similar Lists Detected:")
        for pair in triggers["similar_lists"]:
            print(f"   • {pair['list1']} ↔ {pair['list2']} ({int(pair['similarity']*100)}% similar)")
        print()
    
    # Create alert if Phase 3 is recommended
    if triggers["phase3_recommended"] and triggers["urgency"] in ["medium", "high"]:
        alert = create_phase3_alert()
        added = add_system_upgrade(alert)
        if added:
            print("✅ Phase 3 alert added to system-upgrades list")
            print(f"   Alert ID: {alert['id']}")
        else:
            print("ℹ️ Phase 3 alert already exists in system-upgrades")
        print()
    
    # Summary
    print("=" * 70)
    if triggers["phase3_recommended"]:
        print("⚠️ ACTION RECOMMENDED: Review Phase 3 implementation plan")
        print("   Reference: con_pQh91lSEsCkaqLRz/list_system_implementation_status.md")
    else:
        print("✅ No action needed. List system health is good.")
    print("=" * 70)
    
    # Exit code: 0 = healthy, 1 = warning, 2 = action recommended
    if triggers["urgency"] in ["medium", "high"]:
        sys.exit(2)
    elif triggers["urgency"] == "low":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
