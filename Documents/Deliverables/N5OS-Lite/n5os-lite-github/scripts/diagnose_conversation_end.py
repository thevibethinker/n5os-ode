#!/usr/bin/env python3
"""
Diagnostic Tool for Conversation End Pipeline
Analyzes past conversation closes to identify failure patterns

Usage:
    # Diagnose specific conversation
    python3 diagnose_conversation_end.py --convo-id con_ABC123
    
    # Analyze last N conversations
    python3 diagnose_conversation_end.py --last 10
    
    # Check all conversations with missing titles
    python3 diagnose_conversation_end.py --check-missing-titles
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Paths
USER_WS = Path("/home/workspace")
CONV_DB = USER_WS / "N5/data/conversations.db"
WORKSPACE_ROOT = Path("/home/.z/workspaces")


def check_database() -> bool:
    """Verify database exists and is accessible"""
    if not CONV_DB.exists():
        print(f"❌ Database not found: {CONV_DB}")
        return False
    
    try:
        conn = sqlite3.connect(CONV_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM conversations")
        count = cursor.fetchone()[0]
        print(f"✓ Database accessible: {count} conversations")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def get_conversation(convo_id: str) -> Optional[Dict]:
    """Get conversation from database"""
    try:
        conn = sqlite3.connect(CONV_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM conversations WHERE id = ?
        """, (convo_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
        
    except Exception as e:
        print(f"Error fetching conversation: {e}")
        return None


def get_recent_conversations(limit: int = 10) -> List[Dict]:
    """Get recent conversations"""
    try:
        conn = sqlite3.connect(CONV_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM conversations 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        return []


def get_missing_title_conversations() -> List[Dict]:
    """Get conversations with missing or bad titles"""
    try:
        conn = sqlite3.connect(CONV_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM conversations 
            WHERE status = 'completed' 
            AND (title IS NULL OR title = '' OR title LIKE '%Work Work%')
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    except Exception as e:
        print(f"Error: {e}")
        return []


def check_workspace(convo_id: str) -> Dict:
    """Check conversation workspace"""
    workspace = WORKSPACE_ROOT / convo_id
    
    result = {
        "exists": workspace.exists(),
        "files": [],
        "session_state": False,
        "aar_json": False,
        "aar_md": False,
        "proposed_title": False,
    }
    
    if not result["exists"]:
        return result
    
    # Scan files
    result["files"] = [f.name for f in workspace.iterdir() if f.is_file()]
    result["session_state"] = (workspace / "SESSION_STATE.md").exists()
    
    # Check for AAR files
    aar_json_files = list(workspace.glob("aar-*.json"))
    result["aar_json"] = len(aar_json_files) > 0
    result["aar_json_files"] = [f.name for f in aar_json_files]
    
    result["aar_md"] = (workspace / "AAR.md").exists()
    result["proposed_title"] = (workspace / "PROPOSED_TITLE.md").exists()
    
    return result


def check_archive(convo_id: str) -> Dict:
    """Check if conversation was archived"""
    threads_dir = USER_WS / "N5/logs/threads"
    
    result = {
        "archived": False,
        "archive_path": None,
        "aar_exists": False,
    }
    
    # Look for thread export directory
    for thread_dir in threads_dir.iterdir():
        if thread_dir.is_dir() and convo_id in thread_dir.name:
            result["archived"] = True
            result["archive_path"] = str(thread_dir)
            result["aar_exists"] = (thread_dir / f"aar-{datetime.now().strftime('%Y-%m-%d')}.json").exists()
            break
    
    return result


def diagnose_conversation(convo_id: str):
    """Full diagnostic of a conversation"""
    print(f"\n{'='*70}")
    print(f"DIAGNOSING: {convo_id}")
    print(f"{'='*70}\n")
    
    # Check database
    conv = get_conversation(convo_id)
    if not conv:
        print(f"❌ Conversation not found in database")
        return
    
    print(f"📊 Database Entry:")
    print(f"   Title: {conv.get('title') or '(none)'}")
    print(f"   Status: {conv.get('status')}")
    print(f"   Type: {conv.get('type')}")
    print(f"   Created: {conv.get('created_at')}")
    print(f"   Completed: {conv.get('completed_at') or '(not completed)'}")
    print(f"   AAR Path: {conv.get('aar_path') or '(none)'}")
    
    # Check workspace
    print(f"\n📁 Workspace Check:")
    ws = check_workspace(convo_id)
    if ws["exists"]:
        print(f"   ✓ Workspace exists")
        print(f"   Files: {len(ws['files'])}")
        print(f"   SESSION_STATE.md: {'✓' if ws['session_state'] else '❌'}")
        print(f"   AAR JSON: {'✓' if ws['aar_json'] else '❌'}")
        if ws['aar_json']:
            print(f"     Files: {', '.join(ws.get('aar_json_files', []))}")
        print(f"   AAR.md: {'✓' if ws['aar_md'] else '❌'}")
        print(f"   PROPOSED_TITLE.md: {'✓' if ws['proposed_title'] else '❌'}")
    else:
        print(f"   ❌ Workspace not found")
    
    # Check archive
    print(f"\n📦 Archive Check:")
    archive = check_archive(convo_id)
    if archive["archived"]:
        print(f"   ✓ Thread archived")
        print(f"   Path: {archive['archive_path']}")
        print(f"   AAR: {'✓' if archive['aar_exists'] else '❌'}")
    else:
        print(f"   ❌ No archive found")
    
    # Analysis
    print(f"\n🔍 Analysis:")
    issues = []
    
    if conv.get('status') == 'completed' and not conv.get('title'):
        issues.append("Completed conversation has no title")
    
    if conv.get('title') and 'Work Work' in conv.get('title'):
        issues.append(f"Bad title format: {conv.get('title')}")
    
    if ws["exists"] and ws["proposed_title"]:
        # Check PROPOSED_TITLE content
        title_file = WORKSPACE_ROOT / convo_id / "PROPOSED_TITLE.md"
        content = title_file.read_text()
        if "Work Work" in content:
            issues.append("PROPOSED_TITLE.md contains duplicate words")
    
    if ws["exists"] and not ws["aar_json"] and conv.get('status') == 'completed':
        issues.append("Completed but no AAR JSON generated")
    
    if ws["session_state"] and not ws["aar_json"]:
        issues.append("SESSION_STATE exists but AAR not generated")
    
    if issues:
        for issue in issues:
            print(f"   ⚠️  {issue}")
    else:
        print(f"   ✓ No issues detected")
    
    print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Diagnose conversation end issues")
    parser.add_argument("--convo-id", help="Specific conversation ID to diagnose")
    parser.add_argument("--last", type=int, help="Diagnose last N conversations")
    parser.add_argument("--check-missing-titles", action="store_true",
                       help="Find conversations with missing/bad titles")
    
    args = parser.parse_args()
    
    # Check database first
    if not check_database():
        return 1
    
    if args.convo_id:
        diagnose_conversation(args.convo_id)
    
    elif args.last:
        conversations = get_recent_conversations(args.last)
        print(f"\nDiagnosing {len(conversations)} recent conversations...\n")
        for conv in conversations:
            diagnose_conversation(conv['id'])
    
    elif args.check_missing_titles:
        conversations = get_missing_title_conversations()
        print(f"\n🔍 Found {len(conversations)} conversations with missing/bad titles:\n")
        for conv in conversations:
            diagnose_conversation(conv['id'])
    
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
