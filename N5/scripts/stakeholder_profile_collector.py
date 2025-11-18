#!/usr/bin/env python3
"""
Stakeholder Profile Data Collector (Pure Mechanics)

This script ONLY handles file operations and pattern matching.
All semantic understanding and content generation is done by LLM.

Division of Labor:
- Python: Scan, read, pattern match, write, log
- LLM: Understand, analyze, synthesize, generate content
"""

import json
import re
import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class StakeholderDataCollector:
    """Mechanical data collection - no semantic understanding"""
    
    def __init__(self, meetings_dir: str = "/home/workspace/Personal/Meetings"):
        self.meetings_dir = Path(meetings_dir)
        self.stakeholders_dir = Path("/home/workspace/N5/stakeholders")
        self.db_path = Path("/home/workspace/N5/data/profiles.db")
        
    def scan_b08_files(self) -> List[Dict]:
        """
        Scan for B08_STAKEHOLDER_INTELLIGENCE files.
        Returns list of dicts with file paths and metadata.
        """
        b08_files = []
        
        # Search pattern variations
        patterns = [
            "**/B08_STAKEHOLDER_INTELLIGENCE.md",
            "**/B08_stakeholder_intelligence.md",
            "**/B08_STAKEHOLDER_INTEL.md",
            "**/B08_stakeholder_intel.md"
        ]
        
        for pattern in patterns:
            for b08_path in self.meetings_dir.glob(pattern):
                # Skip if in Archive, Inbox/_quarantine, or Error directories
                if any(x in b08_path.parts for x in ['Archive', '_quarantine', 'Error']):
                    continue
                    
                meeting_dir = b08_path.parent
                
                # Extract date from directory name (mechanical pattern matching)
                date_match = re.match(r'(\d{4}-\d{2}-\d{2})', meeting_dir.name)
                meeting_date = date_match.group(1) if date_match else None
                
                # Find corresponding B01 file
                b01_path = self._find_b01(meeting_dir)
                
                b08_files.append({
                    'b08_path': str(b08_path),
                    'b01_path': str(b01_path) if b01_path else None,
                    'meeting_dir': str(meeting_dir),
                    'meeting_date': meeting_date,
                    'meeting_name': meeting_dir.name
                })
        
        return b08_files
    
    def _find_b01(self, meeting_dir: Path) -> Optional[Path]:
        """Find B01_detailed_recap or B01_DETAILED_RECAP file"""
        patterns = [
            "B01_DETAILED_RECAP.md",
            "B01_detailed_recap.md"
        ]
        
        for pattern in patterns:
            b01_path = meeting_dir / pattern
            if b01_path.exists():
                return b01_path
        return None
    
    def read_stakeholder_data(self, file_paths: List[Dict]) -> List[Dict]:
        """
        Read file contents for each meeting.
        Pure I/O - no understanding.
        """
        data = []
        
        for item in file_paths:
            try:
                # Read B08 content
                b08_content = Path(item['b08_path']).read_text()
                
                # Read B01 content if exists
                b01_content = None
                if item['b01_path']:
                    b01_content = Path(item['b01_path']).read_text()
                
                data.append({
                    **item,
                    'b08_content': b08_content,
                    'b01_content': b01_content
                })
            except Exception as e:
                print(f"Error reading {item['b08_path']}: {e}")
                continue
        
        return data
    
    def extract_email_from_b08(self, b08_content: str) -> Optional[str]:
        """
        Mechanical email extraction from B08 frontmatter or content.
        Just pattern matching - no understanding.
        """
        # Try frontmatter first
        frontmatter_match = re.search(r'email:\s*["\']?([^"\'\n]+)["\']?', b08_content, re.IGNORECASE)
        if frontmatter_match:
            return frontmatter_match.group(1).strip()
        
        # Try email in content
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, b08_content)
        
        if emails:
            # Return first non-V email
            for email in emails:
                if 'vrijen' not in email.lower() and 'careerspan' not in email.lower():
                    return email
        
        return None
    
    def extract_name_from_b08(self, b08_content: str) -> Optional[str]:
        """
        Mechanical name extraction from B08.
        Pattern matching only - no understanding.
        """
        # Try frontmatter
        frontmatter_match = re.search(r'name:\s*["\']?([^"\'\n]+)["\']?', b08_content, re.IGNORECASE)
        if frontmatter_match:
            return frontmatter_match.group(1).strip()
        
        # Try first markdown header
        header_match = re.search(r'^#\s+(.+)$', b08_content, re.MULTILINE)
        if header_match:
            name = header_match.group(1).strip()
            # Clean up common prefixes
            name = re.sub(r'^(B08:|Stakeholder Intelligence:|About:)\s*', '', name, flags=re.IGNORECASE)
            return name.strip()
        
        return None
    
    def group_by_stakeholder(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group meetings by stakeholder (email or name).
        Mechanical grouping - no semantic understanding.
        """
        grouped = defaultdict(list)
        
        for item in data:
            email = self.extract_email_from_b08(item['b08_content'])
            name = self.extract_name_from_b08(item['b08_content'])
            
            # Use email as key if available, otherwise name
            key = email if email else name
            
            if key:
                item['extracted_email'] = email
                item['extracted_name'] = name
                grouped[key].append(item)
        
        return dict(grouped)
    
    def check_existing_profile(self, identifier: str) -> bool:
        """
        Check if stakeholder profile already exists.
        Simple file existence check.
        """
        # Generate filename variations to check
        safe_identifier = re.sub(r'[^a-zA-Z0-9._-]', '_', identifier)
        
        for profile_file in self.stakeholders_dir.glob(f"*{safe_identifier}*.md"):
            return True
        
        return False
    
    def write_profile(self, identifier: str, name: str, content: str) -> Path:
        """
        Write profile to disk.
        Pure I/O - content is generated by LLM.
        """
        # Generate safe filename
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
        safe_id = re.sub(r'[^a-zA-Z0-9._-]', '_', identifier.split('@')[0] if '@' in identifier else identifier)
        
        filename = f"{safe_name}_{safe_id}.md"
        filepath = self.stakeholders_dir / filename
        
        # Ensure directory exists
        self.stakeholders_dir.mkdir(parents=True, exist_ok=True)
        
        # Write file
        filepath.write_text(content)
        
        return filepath
    
    def log_to_database(self, identifier: str, name: str, meetings_count: int, filepath: str):
        """
        Log profile creation to database.
        Pure data recording.
        """
        # Ensure database and table exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stakeholder_profiles (
                identifier TEXT PRIMARY KEY,
                name TEXT,
                filepath TEXT,
                meetings_count INTEGER,
                created_at TEXT,
                last_updated TEXT
            )
        ''')
        
        # Insert or update
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO stakeholder_profiles 
            (identifier, name, filepath, meetings_count, created_at, last_updated)
            VALUES (?, ?, ?, ?, COALESCE((SELECT created_at FROM stakeholder_profiles WHERE identifier = ?), ?), ?)
        ''', (identifier, name, filepath, meetings_count, identifier, now, now))
        
        conn.commit()
        conn.close()
    
    def collect_for_llm_processing(self) -> Dict[str, List[Dict]]:
        """
        Main collection method.
        Returns structured data ready for LLM processing.
        
        Returns:
            Dict mapping stakeholder identifier to list of meeting data
        """
        print("🔍 Scanning for B08_STAKEHOLDER_INTELLIGENCE files...")
        b08_files = self.scan_b08_files()
        print(f"   Found {len(b08_files)} B08 files")
        
        print("📖 Reading file contents...")
        data_with_content = self.read_stakeholder_data(b08_files)
        print(f"   Read {len(data_with_content)} files")
        
        print("👥 Grouping by stakeholder...")
        grouped = self.group_by_stakeholder(data_with_content)
        print(f"   Found {len(grouped)} unique stakeholders")
        
        # Filter out existing profiles
        new_stakeholders = {}
        for identifier, meetings in grouped.items():
            if not self.check_existing_profile(identifier):
                new_stakeholders[identifier] = meetings
        
        print(f"✨ {len(new_stakeholders)} new stakeholders need profiles")
        
        return new_stakeholders


def main():
    """
    Standalone test - just collects and prints data structure.
    Actual LLM processing happens in the workflow that imports this.
    """
    collector = StakeholderDataCollector()
    stakeholders = collector.collect_for_llm_processing()
    
    print("\n📊 Summary:")
    for identifier, meetings in list(stakeholders.items())[:5]:  # Show first 5
        print(f"\n{identifier}:")
        print(f"  - {len(meetings)} meeting(s)")
        for meeting in meetings:
            print(f"    - {meeting['meeting_date']}: {meeting['meeting_name']}")
    
    if len(stakeholders) > 5:
        print(f"\n... and {len(stakeholders) - 5} more stakeholders")


if __name__ == "__main__":
    main()

