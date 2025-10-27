#!/usr/bin/env python3
"""
N5 Timeline Automation Module
Shared logic for detecting and creating system timeline entries

This module is used by both thread-export and conversation-end scripts
to automatically detect timeline-worthy events and prompt for timeline updates.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TimelineDetector:
    """Detects timeline-worthy events from conversation artifacts and AAR data"""
    
    def __init__(self, timeline_path: str = "/home/workspace/N5/timeline/system-timeline.jsonl"):
        self.timeline_path = Path(timeline_path)
        self.timeline_path.parent.mkdir(parents=True, exist_ok=True)
    
    def analyze_aar(self, aar_data: Dict) -> Tuple[bool, Optional[Dict]]:
        """
        Analyze AAR data to determine if timeline entry warranted
        
        Returns: (is_worthy, suggested_entry)
        """
        # Check signals that indicate timeline worthiness
        
        # Signal 1: High impact events
        impact_keywords = [
            'implement', 'create', 'build', 'refactor', 'fix', 'critical',
            'system', 'infrastructure', 'command', 'feature', 'integration'
        ]
        
        title = aar_data.get('title', '').lower()
        purpose = aar_data.get('executive_summary', {}).get('purpose', '').lower()
        outcome = aar_data.get('executive_summary', {}).get('outcome', '').lower()
        
        # Combined text for analysis
        text = f"{title} {purpose} {outcome}"
        
        # Check for impact keywords
        has_impact_keywords = any(kw in text for kw in impact_keywords)
        
        # Signal 2: Multiple artifacts created (indicates substantial work)
        telemetry = aar_data.get('telemetry', {})
        artifact_count = telemetry.get('artifacts_created', 0)
        has_many_artifacts = artifact_count >= 3
        
        # Signal 3: Key events/decisions present
        key_events = aar_data.get('key_events', [])
        has_decisions = len(key_events) >= 2
        
        # Signal 4: New commands/scripts created
        artifacts = aar_data.get('final_state', {}).get('artifacts', [])
        script_artifacts = [a for a in artifacts if a.get('type') in ['script', 'config']]
        created_scripts = len(script_artifacts) >= 1
        
        # Determine if timeline-worthy
        is_worthy = (
            has_impact_keywords or
            has_many_artifacts or
            (has_decisions and created_scripts)
        )
        
        if not is_worthy:
            return False, None
        
        # Generate suggested timeline entry
        suggested_entry = self._generate_suggestion_from_aar(aar_data)
        
        return True, suggested_entry
    
    def _generate_suggestion_from_aar(self, aar_data: Dict) -> Dict:
        """Generate suggested timeline entry from AAR data"""
        
        # Determine category from title and artifacts
        title = aar_data.get('title', '')
        artifacts = aar_data.get('final_state', {}).get('artifacts', [])
        
        category = self._infer_category(title, artifacts)
        
        # Extract components from artifacts
        components = []
        for artifact in artifacts:
            if artifact.get('type') in ['script', 'config', 'document']:
                components.append(artifact['filename'])
        
        # Determine impact level
        impact = self._infer_impact(aar_data)
        
        # Build description from purpose and outcome
        purpose = aar_data.get('executive_summary', {}).get('purpose', '')
        outcome = aar_data.get('executive_summary', {}).get('outcome', '')
        
        if purpose and outcome:
            description = f"{purpose}. {outcome}"
        elif purpose:
            description = purpose
        elif outcome:
            description = outcome
        else:
            description = f"Completed work on {title}"
        
        # Extract tags from key events
        tags = self._extract_tags(aar_data)
        
        return {
            'title': title,
            'description': description,
            'category': category,
            'components': components[:5] if components else None,  # Limit to 5
            'impact': impact,
            'tags': tags[:5] if tags else None,  # Limit to 5
            'status': 'completed'
        }
    
    def _infer_category(self, title: str, artifacts: List[Dict]) -> str:
        """Infer timeline category from title and artifacts"""
        title_lower = title.lower()
        
        # Check for category keywords in title
        if any(kw in title_lower for kw in ['command', 'cmd']):
            return 'command'
        elif any(kw in title_lower for kw in ['fix', 'bug', 'error', 'debug']):
            return 'fix'
        elif any(kw in title_lower for kw in ['infrastructure', 'system', 'architecture']):
            return 'infrastructure'
        elif any(kw in title_lower for kw in ['workflow', 'automation', 'process']):
            return 'workflow'
        elif any(kw in title_lower for kw in ['integration', 'connect', 'api']):
            return 'integration'
        elif any(kw in title_lower for kw in ['ui', 'interface', 'display']):
            return 'ui'
        else:
            # Check artifacts
            script_count = len([a for a in artifacts if a.get('type') == 'script'])
            if script_count >= 2:
                return 'feature'
            return 'infrastructure'
    
    def _infer_impact(self, aar_data: Dict) -> str:
        """Infer impact level from AAR data"""
        # Check for critical/high impact keywords
        text = json.dumps(aar_data).lower()
        
        if any(kw in text for kw in ['critical', 'breaking', 'major', 'significant']):
            return 'high'
        elif any(kw in text for kw in ['minor', 'small', 'fix', 'tweak']):
            return 'low'
        else:
            return 'medium'
    
    def _extract_tags(self, aar_data: Dict) -> List[str]:
        """Extract relevant tags from AAR data"""
        tags = []
        
        # Add category-based tags
        title = aar_data.get('title', '').lower()
        
        tag_keywords = {
            'automation': ['automat', 'workflow'],
            'documentation': ['doc', 'document'],
            'testing': ['test'],
            'refactor': ['refactor', 'reorganiz'],
            'safety': ['safety', 'protect', 'security'],
            'performance': ['performance', 'optimi', 'speed'],
            'aar': ['aar', 'after-action'],
            'timeline': ['timeline'],
            'lessons': ['lesson']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(kw in title for kw in keywords):
                tags.append(tag)
        
        return tags
    
    def analyze_file_changes(self, workspace_path: Path) -> Tuple[bool, Optional[Dict]]:
        """
        Analyze file changes in workspace to detect timeline-worthy events
        Used by conversation-end for lighter-weight detection
        
        Returns: (is_worthy, suggested_entry)
        """
        if not workspace_path.exists():
            return False, None
        
        # Scan for high-signal files
        n5_scripts = list((workspace_path / "N5/scripts").glob("n5_*.py")) if (workspace_path / "N5/scripts").exists() else []
        n5_commands = list((workspace_path / "N5/commands").glob("*.md")) if (workspace_path / "N5/commands").exists() else []
        
        # Check for new commands
        new_commands = []
        for cmd_file in n5_commands:
            # Check if file is very new (modified in last hour as proxy for "new")
            mtime = cmd_file.stat().st_mtime
            age_seconds = datetime.now().timestamp() - mtime
            if age_seconds < 3600:  # Less than 1 hour old
                new_commands.append(cmd_file.name.replace('.md', ''))
        
        # Check for modified critical scripts
        modified_scripts = []
        for script_file in n5_scripts:
            mtime = script_file.stat().st_mtime
            age_seconds = datetime.now().timestamp() - mtime
            if age_seconds < 3600:
                modified_scripts.append(script_file.name)
        
        # Determine if timeline-worthy
        has_new_commands = len(new_commands) > 0
        has_multiple_scripts = len(modified_scripts) >= 2
        
        is_worthy = has_new_commands or has_multiple_scripts
        
        if not is_worthy:
            return False, None
        
        # Generate suggestion
        if has_new_commands:
            title = f"New command(s): {', '.join(new_commands)}"
            description = f"Created {len(new_commands)} new command(s): {', '.join(new_commands)}"
            category = "command"
            components = [f"Recipes/{determine_category(cmd)}/{cmd}.md" for cmd in new_commands]
            impact = "medium"
        else:
            title = "System script updates"
            description = f"Updated {len(modified_scripts)} system scripts"
            category = "infrastructure"
            components = modified_scripts
            impact = "low"
        
        return True, {
            'title': title,
            'description': description,
            'category': category,
            'components': components,
            'impact': impact,
            'status': 'completed',
            'tags': ['automation']
        }
    
    def create_entry(self, title: str, description: str, category: str,
                    version: Optional[str] = None, components: Optional[List[str]] = None,
                    impact: str = "medium", status: str = "completed",
                    tags: Optional[List[str]] = None) -> Dict:
        """Create a timeline entry dict"""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "entry_id": str(uuid.uuid4()),
            "type": "manual" if not version else "versioned",
            "title": title,
            "description": description,
            "category": category,
            "impact": impact,
            "status": status,
            "author": "system"
        }
        
        if version:
            entry["version"] = version
        
        if components:
            entry["components"] = components
        
        if tags:
            entry["tags"] = tags
        
        return entry
    
    def write_entry(self, entry: Dict) -> bool:
        """Write timeline entry to JSONL file"""
        try:
            with open(self.timeline_path, 'a') as f:
                f.write(json.dumps(entry) + '\n')
            return True
        except Exception as e:
            print(f"❌ Error writing to timeline: {e}")
            return False
    
    def prompt_user_for_timeline(self, suggested_entry: Dict, source: str = "thread") -> Optional[Dict]:
        """
        Interactive prompt for user to review and approve timeline entry
        
        Args:
            suggested_entry: Suggested timeline entry dict
            source: Source of detection ("thread" or "conversation-end")
        
        Returns: Approved entry dict or None if skipped
        """
        print("\n" + "="*70)
        print("📊 SYSTEM TIMELINE UPDATE DETECTED")
        print("="*70)
        print(f"\nSource: {source}")
        print(f"\nSuggested timeline entry:")
        print(f"  Title:       {suggested_entry['title']}")
        print(f"  Category:    {suggested_entry['category']}")
        print(f"  Impact:      {suggested_entry['impact']}")
        print(f"  Status:      {suggested_entry['status']}")
        print(f"  Description: {suggested_entry['description'][:100]}...")
        
        if suggested_entry.get('components'):
            print(f"  Components:  {len(suggested_entry['components'])} affected")
            for comp in suggested_entry['components'][:3]:
                print(f"    - {comp}")
            if len(suggested_entry['components']) > 3:
                print(f"    ... and {len(suggested_entry['components']) - 3} more")
        
        if suggested_entry.get('tags'):
            print(f"  Tags:        {', '.join(suggested_entry['tags'])}")
        
        print("\n" + "-"*70)
        print("Options:")
        print("  Y - Add to timeline as-is")
        print("  e - Edit before adding")
        print("  n - Skip (don't add to timeline)")
        print("-"*70)
        
        response = input("\nAdd to system timeline? (Y/e/n): ").strip().lower()
        
        if response in ['n', 'no', 'skip']:
            print("→ Skipped timeline update")
            return None
        
        if response in ['e', 'edit']:
            print("\n📝 Edit timeline entry (press Enter to keep current value):\n")
            
            # Edit title
            new_title = input(f"Title [{suggested_entry['title']}]: ").strip()
            if new_title:
                suggested_entry['title'] = new_title
            
            # Edit description
            new_desc = input(f"Description [{suggested_entry['description'][:50]}...]: ").strip()
            if new_desc:
                suggested_entry['description'] = new_desc
            
            # Edit category
            print(f"Category options: infrastructure, feature, command, workflow, ui, integration, fix")
            new_category = input(f"Category [{suggested_entry['category']}]: ").strip()
            if new_category:
                suggested_entry['category'] = new_category
            
            # Edit impact
            new_impact = input(f"Impact (low/medium/high) [{suggested_entry['impact']}]: ").strip()
            if new_impact:
                suggested_entry['impact'] = new_impact
            
            print("\n✓ Entry updated")
        
        # Create and return final entry
        entry = self.create_entry(
            title=suggested_entry['title'],
            description=suggested_entry['description'],
            category=suggested_entry['category'],
            components=suggested_entry.get('components'),
            impact=suggested_entry['impact'],
            status=suggested_entry['status'],
            tags=suggested_entry.get('tags')
        )
        
        return entry


def add_timeline_entry_from_aar(aar_data: Dict) -> bool:
    """
    Main entry point for thread-export integration
    Analyzes AAR and prompts for timeline entry if worthy
    
    Returns: True if entry was added, False otherwise
    """
    detector = TimelineDetector()
    
    is_worthy, suggested_entry = detector.analyze_aar(aar_data)
    
    if not is_worthy:
        print("→ Thread not significant for system timeline")
        return False
    
    # Prompt user
    approved_entry = detector.prompt_user_for_timeline(suggested_entry, source="thread-export")
    
    if not approved_entry:
        return False
    
    # Write entry
    success = detector.write_entry(approved_entry)
    
    if success:
        print(f"\n✅ System timeline updated: {approved_entry['title']}")
        print(f"   Entry ID: {approved_entry['entry_id']}")
        print(f"   Timestamp: {approved_entry['timestamp']}")
    
    return success


def add_timeline_entry_from_workspace(workspace_path: Path) -> bool:
    """
    Main entry point for conversation-end integration
    Scans workspace for high-signal changes
    
    Returns: True if entry was added, False otherwise
    """
    detector = TimelineDetector()
    
    is_worthy, suggested_entry = detector.analyze_file_changes(workspace_path)
    
    if not is_worthy:
        return False
    
    # Prompt user
    approved_entry = detector.prompt_user_for_timeline(suggested_entry, source="conversation-end")
    
    if not approved_entry:
        return False
    
    # Write entry
    success = detector.write_entry(approved_entry)
    
    if success:
        print(f"\n✅ System timeline updated: {approved_entry['title']}")
        print(f"   Entry ID: {approved_entry['entry_id']}")
    
    return success
