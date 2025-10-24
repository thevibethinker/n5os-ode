#!/usr/bin/env python3
"""
N5 Thread Export - After-Action Report (AAR) Generator
Generate comprehensive AAR for conversation threads (AAR v2.0 protocol)

Usage:
    python3 n5_thread_export.py [thread_id] [--title "Title"] [--dry-run]
    python3 n5_thread_export.py --auto  # Auto-detect current thread
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
import tempfile  # For atomic writes

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

# Timeline automation integration
try:
    from timeline_automation import add_timeline_entry_from_aar
    TIMELINE_AVAILABLE = True
except ImportError:
    TIMELINE_AVAILABLE = False

# Title generation
try:
    from n5_title_generator import TitleGenerator
    TITLE_GENERATOR_AVAILABLE = True
except ImportError:
    TITLE_GENERATOR_AVAILABLE = False

# Paths
ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
LOGS_DIR = ROOT / "logs" / "threads"
CONVERSATION_WS_ROOT = Path("/home/.z/workspaces")
AAR_SCHEMA_PATH = SCHEMAS / "aar.schema.json"
LESSONS_DIR = ROOT / "lessons" / "archive"

# Constants
AAR_VERSION = "2.2"

# Display/formatting constants
MAX_PREVIEW_ARTIFACTS = 3
MAX_NEXT_STEPS_DISPLAY = 5
MAX_FILES_IN_TREE = 10
MAX_DECISIONS_DISPLAY = 5


class ThreadExporter:
    """Handles AAR generation and thread export"""
    
    def __init__(self, thread_id: str, title: Optional[str] = None, dry_run: bool = False):
        self.thread_id = thread_id
        self.title = title
        self.dry_run = dry_run
        self.auto_confirm = False  # For automated execution
        self.is_checkpoint = False  # For progressive documentation
        self.conversation_ws = CONVERSATION_WS_ROOT / thread_id
        self.aar_data = {}
        self.artifacts = []
        
        # Archive directory (new chronological naming convention)
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d-%H%M")
        thread_suffix = thread_id[-4:] if len(thread_id) >= 4 else thread_id
        
        if title:
            safe_title = self._sanitize_title(title)
            self.archive_dir = LOGS_DIR / f"{timestamp}_{safe_title}_{thread_suffix}"
        else:
            # Auto-generate title from conversation type
            auto_title = "conversation"  # Will be improved by detect_conversation_type later
            safe_title = self._sanitize_title(auto_title)
            self.archive_dir = LOGS_DIR / f"{timestamp}_{safe_title}_{thread_suffix}"
        
        self.aar_json_path = self.archive_dir / f"aar-{datetime.now().strftime('%Y-%m-%d')}.json"
        self.aar_md_path = self.archive_dir / f"aar-{datetime.now().strftime('%Y-%m-%d')}.md"
        self.artifacts_dir = self.archive_dir / "artifacts"
        self.checkpoint_path = self.archive_dir / f"checkpoint-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.json"
    
    def _sanitize_title(self, title: str) -> str:
        """Convert title to filesystem-safe string (preserves readability)"""
        import re
        # Remove filesystem-unsafe characters only
        safe = re.sub(r'[<>:"/\\|?*]', '', title)
        # Replace spaces with hyphens
        safe = safe.replace(' ', '-')
        # Collapse multiple hyphens
        safe = re.sub(r'-+', '-', safe)
        # Remove leading/trailing hyphens
        safe = safe.strip('-')
        # Limit length (increased from 60 to 80)
        return safe[:80]
    
    def detect_thread_id(self) -> Optional[str]:
        """Auto-detect current conversation thread ID"""
        if not CONVERSATION_WS_ROOT.exists():
            return None
        
        # Find most recently modified con_* directory
        con_dirs = sorted(
            [d for d in CONVERSATION_WS_ROOT.iterdir() 
             if d.is_dir() and d.name.startswith("con_")],
            key=lambda d: d.stat().st_mtime,
            reverse=True
        )
        
        if con_dirs:
            return con_dirs[0].name
        return None
    
    def validate_thread(self) -> bool:
        """Check if thread workspace exists"""
        if not self.conversation_ws.exists():
            print(f"❌ Thread workspace not found: {self.conversation_ws}")
            return False
        return True
    
    def inventory_artifacts(self) -> List[Dict]:
        """Scan conversation workspace for artifacts"""
        artifacts = []
        
        if not self.conversation_ws.exists():
            return artifacts
        
        for filepath in self.conversation_ws.rglob("*"):
            if filepath.is_file():
                stat = filepath.stat()
                artifacts.append({
                    "filename": filepath.name,
                    "path": filepath,
                    "relative_path": filepath.relative_to(self.conversation_ws),
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                    "type": self._classify_file(filepath)
                })
        
        return artifacts
    
    def _classify_file(self, filepath: Path) -> str:
        """Classify file by extension"""
        ext = filepath.suffix.lower()
        
        if ext in ['.py', '.sh', '.js', '.ts']:
            return "script"
        elif ext in ['.md', '.txt', '.pdf', '.docx']:
            return "document"
        elif ext in ['.json', '.jsonl', '.csv', '.yaml', '.yml']:
            return "data"
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
            return "image"
        elif ext in ['.toml', '.ini', '.conf', '.cfg']:
            return "config"
        else:
            return "other"
    
    # ===== HELPER METHODS FOR MODULAR EXPORTS =====
    
    def _get_purpose(self, aar_data: Dict) -> str:
        """Extract purpose from AAR data"""
        return aar_data.get('executive_summary', {}).get('purpose', 'Thread work')
    
    def _get_outcome(self, aar_data: Dict) -> str:
        """Extract outcome from AAR data"""
        return aar_data.get('executive_summary', {}).get('outcome', 'Work completed')
    
    def _get_constraints(self, aar_data: Dict) -> List[str]:
        """Extract constraints from AAR data"""
        return aar_data.get('executive_summary', {}).get('constraints', [])
    
    def _get_artifacts_by_type(self, artifacts: List[Dict]) -> Dict[str, List[Dict]]:
        """Group artifacts by type"""
        by_type = {}
        for artifact in artifacts:
            atype = artifact.get('type', 'other')
            by_type.setdefault(atype, []).append(artifact)
        return by_type
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable form"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def ask_interactive_questions(self) -> Dict:
        """Ask user 5 key questions for AAR"""
        print("\n" + "="*70)
        print("AFTER-ACTION REPORT (AAR) - Interactive Questions")
        print("="*70)
        print("\nPlease answer the following questions to generate the AAR:")
        print("(This helps capture the narrative context we can't access programmatically)\n")
        
        responses = {}
        
        # Question 1: Objective
        print("1. What was the PRIMARY OBJECTIVE of this conversation?")
        print("   (What were you trying to accomplish?)")
        responses['objective'] = input("   → ").strip()
        
        # Question 2: Key Decisions
        print("\n2. What were 2-3 KEY DECISIONS made during this conversation?")
        print("   (Important choices, directions taken)")
        print("   Enter decisions one per line. Press Enter twice when done.")
        decisions = []
        while True:
            decision = input("   → ").strip()
            if not decision:
                break
            decisions.append(decision)
        responses['decisions'] = decisions
        
        # Question 3: Outcomes
        print("\n3. What were the MAIN OUTCOMES/DELIVERABLES?")
        print("   (What was created, accomplished, or learned?)")
        responses['outcomes'] = input("   → ").strip()
        
        # Question 4: Next Steps
        print("\n4. What should happen NEXT?")
        print("   (Primary continuation objective)")
        responses['next_objective'] = input("   → ").strip()
        
        # Question 5: Challenges/Pivots
        print("\n5. Were there any significant CHALLENGES or PIVOTS?")
        print("   (Optional - press Enter to skip)")
        responses['challenges'] = input("   → ").strip()
        
        return responses
    
    def generate_aar_data(self, interactive_responses: Dict) -> Dict:
        """Generate AAR JSON structure"""
        now = datetime.now(timezone.utc)
        
        # Build key events from decisions
        key_events = []
        for idx, decision in enumerate(interactive_responses.get('decisions', []), 1):
            key_events.append({
                "description": decision,
                "rationale": "Key decision made during conversation",
                "type": "decision"
            })
        
        # Add challenges as events if provided
        if interactive_responses.get('challenges'):
            key_events.append({
                "description": interactive_responses['challenges'],
                "rationale": "Challenge or pivot encountered",
                "type": "challenge"
            })
        
        # Build artifacts list
        artifacts_data = []
        for artifact in self.artifacts:
            artifacts_data.append({
                "filename": str(artifact['relative_path']),
                "description": f"{artifact['type'].capitalize()} file created during conversation",
                "type": artifact['type'],
                "size_bytes": artifact['size_bytes'],
                "created_at": artifact['created_at'],
                "modified_at": artifact['modified_at']
            })
        
        # Generate next steps from objective
        next_steps = []
        if interactive_responses.get('next_objective'):
            next_steps.append({
                "action": interactive_responses['next_objective'],
                "details": "Primary continuation objective from AAR",
                "priority": "H"
            })
        
        # Build AAR structure
        aar = {
            "thread_id": self.thread_id,
            "archived_date": now.strftime("%Y-%m-%d"),
            "title": self.title or f"Conversation {self.thread_id}",
            "executive_summary": {
                "purpose": interactive_responses.get('objective', 'No objective specified'),
                "outcome": interactive_responses.get('outcomes', 'No outcomes specified')
            },
            "key_events": key_events if key_events else [{
                "description": "No key events captured",
                "rationale": "Interactive responses not provided",
                "type": "milestone"
            }],
            "final_state": {
                "summary": f"Created {len(artifacts_data)} artifacts during conversation",
                "artifacts": artifacts_data
            },
            "primary_objective": interactive_responses.get('next_objective', 'No next objective specified'),
            "next_steps": next_steps if next_steps else [{
                "action": "Review AAR and determine next steps",
                "details": "No specific next steps defined"
            }],
            "aar_version": AAR_VERSION,
            "telemetry": {
                "artifacts_created": len(artifacts_data),
                "total_size_bytes": sum(a['size_bytes'] for a in self.artifacts),
                "aar_generated_by": "Vrijen The Vibe Strategist (Zo)",
                "aar_generation_method": "interactive"
            },
            "metadata": {
                "ended_at": now.isoformat()
            }
        }
        
        return aar
    
    def validate_aar(self, aar_data: Dict) -> Tuple[bool, List[str]]:
        """Validate AAR against schema"""
        if not AAR_SCHEMA_PATH.exists():
            return False, [f"Schema not found: {AAR_SCHEMA_PATH}"]
        
        with open(AAR_SCHEMA_PATH) as f:
            schema = json.load(f)
        
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(aar_data), key=lambda e: e.path)
        
        if errors:
            error_messages = []
            for e in errors:
                path = '.'.join(map(str, e.path)) or '<root>'
                error_messages.append(f"  - {path}: {e.message}")
            return False, error_messages
        
        return True, []
    
    def _load_thread_lessons(self) -> List[Dict]:
        """Load lessons for this thread from N5/lessons/archive/*.lessons.jsonl"""
        lessons = []
        try:
            if not LESSONS_DIR.exists():
                return lessons
            # glob possible monthly or dated files containing this thread_id
            for f in LESSONS_DIR.glob("*.lessons.jsonl"):
                try:
                    for line in f.read_text().splitlines():
                        if not line.strip():
                            continue
                        obj = json.loads(line)
                        if obj.get("thread_id") == self.thread_id:
                            lessons.append(obj)
                except Exception:
                    continue
        except Exception:
            pass
        return lessons

    def generate_markdown(self, aar_data: Dict) -> str:
        """Generate markdown view from AAR JSON (dual-write pattern)"""
        md = []
        
        # Header
        md.append(f"# After-Action Report: {aar_data['title']}")
        md.append(f"\n**Thread ID:** `{aar_data['thread_id']}`  ")
        md.append(f"**Archived:** {aar_data['archived_date']}  ")
        md.append(f"**AAR Version:** {aar_data['aar_version']}  ")
        md.append(f"\n---\n")
        
        # Executive Summary
        md.append("## Executive Summary\n")
        md.append(f"**Purpose:** {aar_data['executive_summary']['purpose']}\n")
        md.append(f"**Outcome:** {aar_data['executive_summary']['outcome']}\n")
        if aar_data['executive_summary'].get('context'):
            md.append(f"**Context:** {aar_data['executive_summary']['context']}\n")
        
        # Key Events
        md.append("\n## Key Events & Decisions\n")
        for idx, event in enumerate(aar_data['key_events'], 1):
            event_type = event.get('type', 'event').upper()
            md.append(f"{idx}. **[{event_type}]** {event['description']}")
            if event.get('rationale'):
                md.append(f"   - *Rationale:* {event['rationale']}")
            md.append("")
        
        # Lessons (if any)
        lessons = aar_data.get('metadata', {}).get('lessons', [])
        if lessons:
            md.append("\n## Lessons Learned (auto-imported)\n")
            for i, les in enumerate(lessons[:10], 1):
                md.append(f"- [{les.get('type','lesson')}] {les.get('title','(untitled)')}: {les.get('description','').strip()[:300]}")
        
        # Final State
        md.append("\n## Final State\n")
        md.append(f"{aar_data['final_state']['summary']}\n")
        
        if aar_data['final_state']['artifacts']:
            md.append("### Artifacts\n")
            for artifact in aar_data['final_state']['artifacts']:
                size_kb = artifact['size_bytes'] / 1024
                md.append(f"- **`{artifact['filename']}`** ({artifact['type']}, {size_kb:.1f} KB)")
                md.append(f"  - {artifact['description']}")
        
        # Primary Objective
        md.append(f"\n## Primary Objective for Next Thread\n")
        md.append(f"{aar_data['primary_objective']}\n")
        
        # Next Steps
        md.append("## Actionable Next Steps\n")
        for idx, step in enumerate(aar_data['next_steps'], 1):
            priority = step.get('priority', '')
            priority_str = f" **[{priority}]**" if priority else ""
            md.append(f"{idx}.{priority_str} **{step['action']}**")
            if step.get('details'):
                md.append(f"   - {step['details']}")
            if step.get('estimated_duration'):
                md.append(f"   - *Est. duration:* {step['estimated_duration']}")
            md.append("")
        
        # Metadata (collapsed)
        if aar_data.get('telemetry'):
            md.append("\n---\n")
            md.append("<details>")
            md.append("<summary>Metadata & Telemetry</summary>\n")
            md.append("```json")
            md.append(json.dumps(aar_data.get('telemetry', {}), indent=2))
            if aar_data.get('metadata'):
                md.append(json.dumps(aar_data.get('metadata', {}), indent=2))
            md.append("```")
            md.append("</details>")
        
        return '\n'.join(md)
    
    def copy_artifacts(self):
        """Copy artifacts from conversation workspace to archive"""
        if not self.artifacts:
            print("  No artifacts to copy")
            return
        
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        for artifact in self.artifacts:
            src = artifact['path']
            dest = self.artifacts_dir / artifact['relative_path']
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            if not self.dry_run:
                shutil.copy2(src, dest)
            print(f"  {'[DRY-RUN]' if self.dry_run else '✓'} Copied: {artifact['filename']}")
    
    def discover_artifacts(self):
        """Wrapper method for inventory_artifacts"""
        self.artifacts = self.inventory_artifacts()
    
    def inventory_recent_workspace_artifacts(self, lookback_hours: int = 6) -> List[Dict]:
        """Scan key workspace dirs for recently modified files to improve title specificity."""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=lookback_hours)
        recent: List[Dict] = []
        scan_dirs = [
            ROOT / "N5" / "scripts",
            ROOT / "N5" / "docs",
            ROOT / "N5" / "prefs",
            ROOT / "N5" / "commands",
        ]
        for d in scan_dirs:
            if not d.exists():
                continue
            for fp in d.rglob("*"):
                if not fp.is_file():
                    continue
                try:
                    mtime = datetime.fromtimestamp(fp.stat().st_mtime, tz=timezone.utc)
                    if mtime >= cutoff:
                        recent.append({
                            "filename": fp.name,
                            "path": fp,
                            "relative_path": fp.relative_to(ROOT),
                            "size_bytes": fp.stat().st_size,
                            "created_at": datetime.fromtimestamp(fp.stat().st_ctime, tz=timezone.utc).isoformat(),
                            "modified_at": mtime.isoformat(),
                            "type": self._classify_file(fp)
                        })
                except Exception:
                    continue
        return recent

    def generate_smart_aar(self) -> Dict:
        """Generate intelligent AAR using content extraction (Phase 3)"""
        smart_responses = {
            'objective': self.extract_objective_from_artifacts(),
            'decisions': self.extract_key_decisions(),
            'outcomes': self.generate_smart_summary(),
            'next_objective': self.infer_next_steps(),
            'challenges': ''  # No way to infer challenges programmatically yet
        }
        aar = self.generate_aar_data(smart_responses)
        # Attach lessons (non-schema field under metadata)
        try:
            lessons = self._load_thread_lessons()
            if lessons:
                aar.setdefault('metadata', {})['lessons'] = lessons
        except Exception:
            pass
        return aar
    
    def generate_interactive_aar(self) -> Dict:
        """Generate AAR through interactive questions"""
        responses = self.ask_interactive_questions()
        return self.generate_aar_data(responses)
    
    def generate_dummy_aar(self) -> Dict:
        """Generate minimal AAR with dummy data for testing"""
        dummy_responses = {
            'objective': 'Thread objective (to be filled interactively)',
            'decisions': ['Decision 1 (to be filled)', 'Decision 2 (to be filled)'],
            'outcomes': 'Outcomes (to be filled interactively)',
            'next_objective': 'Next objective (to be filled interactively)',
            'challenges': ''
        }
        return self.generate_aar_data(dummy_responses)
    
    # ===== PHASE 3: SMART CONTENT EXTRACTION =====
    
    def detect_conversation_type(self) -> str:
        """Detect conversation type from artifacts and title"""
        if not self.artifacts:
            return "general"
        
        title_lower = (self.title or "").lower()
        
        # Count artifact types
        scripts = [a for a in self.artifacts if a['type'] == 'script']
        docs = [a for a in self.artifacts if a['type'] == 'document']
        data_files = [a for a in self.artifacts if a['type'] == 'data']
        
        # Bug fix indicators
        if any(x in title_lower for x in ['bug', 'fix', 'debug', 'error']):
            return "bugfix"
        
        # Implementation indicators
        if len(scripts) >= 2 and any('test' in a['filename'].lower() for a in self.artifacts):
            return "implementation"
        
        # Research indicators  
        if len(docs) > len(scripts) and len(docs) >= 3:
            return "research"
        
        # Data analysis indicators
        if len(data_files) >= 2 and any(x in title_lower for x in ['analysis', 'report', 'data']):
            return "analysis"
        
        # Strategy/planning indicators
        if any(x in title_lower for x in ['strategy', 'plan', 'design', 'architecture']):
            return "strategy"
        
        return "general"
    
    def extract_objective_from_artifacts(self) -> str:
        """Infer conversation objective from artifacts and patterns"""
        if not self.artifacts:
            return "Work session with no artifacts created"
        
        conv_type = self.detect_conversation_type()
        title = self.title or "conversation"
        
        # Type-specific objective templates
        if conv_type == "implementation":
            script_count = len([a for a in self.artifacts if a['type'] == 'script'])
            return f"Implement {title} with {script_count} script(s) and supporting artifacts"
        
        elif conv_type == "research":
            doc_count = len([a for a in self.artifacts if a['type'] == 'document'])
            return f"Research and document findings on {title} ({doc_count} documents created)"
        
        elif conv_type == "bugfix":
            return f"Debug and fix issue: {title}"
        
        elif conv_type == "analysis":
            return f"Analyze data and generate insights for {title}"
        
        elif conv_type == "strategy":
            return f"Strategic planning and decision-making for {title}"
        
        else:
            # Generic objective based on artifacts
            artifact_types = set(a['type'] for a in self.artifacts)
            types_str = ", ".join(artifact_types)
            return f"Create and organize {types_str} artifacts for {title}"
    
    def extract_key_decisions(self) -> List[str]:
        """Extract key decisions from artifact analysis"""
        decisions = []
        conv_type = self.detect_conversation_type()
        
        # Decision 1: Conversation type/approach
        type_descriptions = {
            "implementation": "Chose implementation approach with scripts and testing",
            "research": "Conducted research-based exploration with documentation",
            "bugfix": "Diagnosed and implemented bug fix",
            "analysis": "Performed data analysis with structured outputs",
            "strategy": "Developed strategic plan with decision framework",
            "general": "Completed general work session"
        }
        decisions.append(type_descriptions.get(conv_type, "Completed work session"))
        
        # Decision 2: File organization pattern
        if len(self.artifacts) > 5:
            decisions.append(f"Organized work into {len(self.artifacts)} discrete artifacts")
        elif len(self.artifacts) > 0:
            decisions.append(f"Created focused set of {len(self.artifacts)} artifact(s)")
        
        # Decision 3: Technology/tools (if scripts present)
        scripts = [a for a in self.artifacts if a['type'] == 'script']
        if scripts:
            extensions = set(Path(a['filename']).suffix for a in scripts)
            tech = {'.py': 'Python', '.sh': 'Bash', '.js': 'JavaScript', '.ts': 'TypeScript'}
            techs = [tech.get(ext, ext) for ext in extensions if ext in tech]
            if techs:
                decisions.append(f"Used {', '.join(techs)} for implementation")
        
        return decisions[:3]  # Limit to 3 key decisions
    
    def generate_smart_summary(self) -> str:
        """Generate intelligent outcome summary from artifacts"""
        if not self.artifacts:
            return "Conversation completed with no artifacts generated"
        
        conv_type = self.detect_conversation_type()
        artifact_count = len(self.artifacts)
        total_size = sum(a['size_bytes'] for a in self.artifacts)
        size_kb = total_size / 1024
        
        # Group artifacts by type
        by_type = {}
        for a in self.artifacts:
            by_type.setdefault(a['type'], []).append(a)
        
        type_summary = ", ".join(f"{len(v)} {k}(s)" for k, v in by_type.items())
        
        # Type-specific summaries
        if conv_type == "implementation":
            return f"Completed implementation with {type_summary} totaling {size_kb:.1f}KB. System ready for testing."
        
        elif conv_type == "research":
            return f"Research completed with {type_summary}. Documentation captures findings and insights."
        
        elif conv_type == "bugfix":
            return f"Bug fix implemented and documented with {type_summary}."
        
        elif conv_type == "analysis":
            return f"Analysis completed with {type_summary} containing results and visualizations."
        
        elif conv_type == "strategy":
            return f"Strategic plan developed with {type_summary} capturing decisions and rationale."
        
        else:
            return f"Created {artifact_count} artifacts ({type_summary}) totaling {size_kb:.1f}KB"
    
    def infer_next_steps(self) -> str:
        """Infer logical next steps based on conversation type and artifacts"""
        conv_type = self.detect_conversation_type()
        
        # Type-specific next steps
        next_steps = {
            "implementation": "Test implementation, integrate with existing systems, document usage",
            "research": "Review findings, share with stakeholders, determine action items",
            "bugfix": "Verify fix works, deploy to production, add regression tests",
            "analysis": "Review analysis results, make data-driven decisions, create action plan",
            "strategy": "Execute strategic plan, assign responsibilities, set milestones",
            "general": "Review work completed, determine next priorities"
        }
        
        return next_steps.get(conv_type, "Continue development based on session outcomes")
    
    def generate_smart_aar(self) -> Dict:
        """Generate intelligent AAR using content extraction (Phase 3)"""
        smart_responses = {
            'objective': self.extract_objective_from_artifacts(),
            'decisions': self.extract_key_decisions(),
            'outcomes': self.generate_smart_summary(),
            'next_objective': self.infer_next_steps(),
            'challenges': ''  # No way to infer challenges programmatically yet
        }
        aar = self.generate_aar_data(smart_responses)
        # Attach lessons (non-schema field under metadata)
        try:
            lessons = self._load_thread_lessons()
            if lessons:
                aar.setdefault('metadata', {})['lessons'] = lessons
        except Exception:
            pass
        return aar
    
    # ===== PHASE 3B: PROGRESSIVE DOCUMENTATION =====
    
    def save_checkpoint(self):
        """Save progressive AAR checkpoint (draft)"""
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.dry_run:
            with open(self.checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(self.aar_data, f, indent=2, ensure_ascii=False)
        
        print(f"  {'[DRY-RUN]' if self.dry_run else '✓'} Saved checkpoint: {self.checkpoint_path.name}")
        return self.checkpoint_path
    
    def load_latest_checkpoint(self) -> Optional[Dict]:
        """Load most recent checkpoint for this thread"""
        if not self.archive_dir.exists():
            return None
        
        # Find all checkpoint files
        checkpoints = sorted(self.archive_dir.glob("checkpoint-*.json"))
        if not checkpoints:
            return None
        
        latest = checkpoints[-1]
        print(f"  Loading checkpoint: {latest.name}")
        
        with open(latest, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def merge_checkpoint_data(self, checkpoint: Dict) -> Dict:
        """Merge checkpoint data with current session"""
        # Start with current smart extraction
        current = self.generate_smart_aar()
        
        # Merge key events (combine lists, dedupe)
        checkpoint_events = checkpoint.get('key_events', [])
        current_events = current.get('key_events', [])
        
        # Merge artifacts (use current, as it's fresher)
        # But preserve checkpoint's executive summary if more detailed
        if len(checkpoint['executive_summary']['purpose']) > len(current['executive_summary']['purpose']):
            current['executive_summary'] = checkpoint['executive_summary']
        
        # Combine key events
        all_events = checkpoint_events + current_events
        current['key_events'] = all_events[:20]  # Limit to schema max
        
        return current
    
    # ===== MODULAR EXPORT GENERATION (v2.2) =====
    
    def generate_modular_exports(self, aar_data: Dict, next_thread_title: Optional[str] = None) -> Dict[str, str]:
        """Generate modular markdown exports (v2.2 - 5-phase aligned)"""
        return {
            'INDEX.md': self._generate_index_md(aar_data),
            'RESUME.md': self._generate_resume_md(aar_data, next_thread_title),
            'DESIGN.md': self._generate_design_md(aar_data),
            'IMPLEMENTATION.md': self._generate_implementation_md(aar_data),
            'VALIDATION.md': self._generate_validation_md(aar_data),
            'CONTEXT.md': self._generate_context_md(aar_data)
        }
    
    def _generate_index_md(self, aar_data: Dict) -> str:
        """Generate INDEX.md - Navigation hub"""
        thread_id = self.thread_id
        export_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        topic = self._get_purpose(aar_data)
        if len(topic) > 80:
            topic = topic[:77] + "..."
        status = aar_data.get('status', 'Complete')
        artifacts = self.artifacts
        
        md = []
        md.append(f"# Thread Export Index")
        md.append(f"\n**Thread:** {thread_id}  ")
        md.append(f"**Date:** {export_date}  ")
        md.append(f"**Topic:** {topic}  ")
        md.append(f"**Status:** {status}  ")
        md.append(f"\n---\n")
        
        md.append("## File Directory\n")
        md.append("| File | Purpose | Primary Audience |")
        md.append("|------|---------|------------------|")
        md.append("| **RESUME.md** | Quick resume entry point | Resuming work |")
        md.append("| **DESIGN.md** | Decisions & rationale | Understanding choices |")
        md.append("| **IMPLEMENTATION.md** | Technical details | Implementation |")
        md.append("| **VALIDATION.md** | Testing & troubleshooting | Debugging |")
        md.append("| **CONTEXT.md** | Historical context | Background research |")
        md.append("| **INDEX.md** | This file - navigation | Overview |")
        
        md.append("\n## Quick Start Workflow\n")
        md.append("1. **Start here** - Read this INDEX")
        md.append("2. **RESUME.md** - Get oriented (10-minute workflow)")
        md.append("3. **DESIGN.md** - Understand key decisions")
        md.append("4. **IMPLEMENTATION.md** - Technical implementation")
        md.append("5. **VALIDATION.md** - If issues arise")
        md.append("6. **CONTEXT.md** - For historical background")
        
        md.append("\n## File Statistics\n")
        total_size = sum(a['size_bytes'] for a in artifacts)
        md.append(f"- Total artifacts: {len(artifacts)}")
        md.append(f"- Total size: {self._format_file_size(total_size)}")
        md.append(f"- Export format: AAR v{AAR_VERSION}")
        
        md.append("\n---\n")
        md.append(f"*Generated by Zo Thread Export System v{AAR_VERSION}*")
        
        return '\n'.join(md)
    
    def _generate_resume_md(self, aar_data: Dict, next_thread_title: Optional[str] = None) -> str:
        """Generate RESUME.md - Quick resume entry point"""
        thread_id = self.thread_id
        export_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        topic = self._get_purpose(aar_data)
        status = aar_data.get('status', 'Complete')
        outcome = self._get_outcome(aar_data)
        artifacts = aar_data.get('final_state', {}).get('artifacts', [])
        next_steps = aar_data.get('next_steps', [])
        
        md = []
        md.append(f"# Thread Resume")
        md.append(f"\n**Thread ID:** {thread_id}  ")
        md.append(f"**Date:** {export_date}  ")
        md.append(f"**Status:** {status}  ")
        md.append(f"\n---\n")
        
        md.append("## Summary\n")
        md.append(f"**Purpose:** {topic}\n")
        md.append(f"**Outcome:** {outcome}\n")
        
        md.append("\n## Quick Start (10 Minutes)\n")
        md.append("1. Read this summary (2 min)")
        md.append("2. Review what was completed (3 min)")
        md.append("3. Check next steps (2 min)")
        md.append("4. Start with highest priority action (3 min)")
        
        md.append("\n## What Was Completed\n")
        if artifacts:
            by_type = self._get_artifacts_by_type(artifacts)
            for atype, items in list(by_type.items())[:MAX_PREVIEW_ARTIFACTS]:
                md.append(f"### {atype.capitalize()} Files ({len(items)})")
                for item in items[:3]:
                    size = self._format_file_size(item['size_bytes'])
                    md.append(f"- `{item['filename']}` ({size})")
                if len(items) > 3:
                    md.append(f"  *(+{len(items) - 3} more)*")
                md.append("")
        
        md.append("\n## Next Steps\n")
        for idx, step in enumerate(next_steps[:MAX_NEXT_STEPS_DISPLAY], 1):
            priority = step.get('priority', '')
            priority_str = f" **[{priority}]**" if priority else ""
            md.append(f"{idx}.{priority_str} {step['action']}")
            if step.get('details'):
                md.append(f"   - {step['details']}")
        
        # Add next thread title suggestion
        if next_thread_title:
            md.append("\n---\n")
            md.append("## 🔗 Resume in New Thread\n")
            md.append(f"**Suggested Thread Title:** `{next_thread_title}`\n")
            md.append("*Zo: When starting the next thread to continue this work, please name the thread:*\n")
            md.append(f"**\"{next_thread_title}\"**\n")
            md.append("\n*This ensures consistent sequential numbering and linkage between related threads.*")
        
        md.append("\n---\n")
        md.append("*For full details, see IMPLEMENTATION.md and DESIGN.md*")
        
        return '\n'.join(md)
    
    def _generate_design_md(self, aar_data: Dict) -> str:
        """Generate DESIGN.md - Decisions and rationale"""
        thread_id = self.thread_id
        export_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        key_events = aar_data.get('key_events', [])
        constraints = self._get_constraints(aar_data)
        
        md = []
        md.append(f"# Design & Decisions")
        md.append(f"\n**Thread ID:** {thread_id}  ")
        md.append(f"**Date:** {export_date}  ")
        md.append(f"\n---\n")
        
        if constraints:
            md.append("## Critical Constraints\n")
            for constraint in constraints:
                md.append(f"- {constraint}")
            md.append("")
        
        md.append("## Key Technical Decisions\n")
        for idx, event in enumerate(key_events[:MAX_DECISIONS_DISPLAY], 1):
            event_type = event.get('type', 'decision').upper()
            md.append(f"### Decision {idx}: {event['description']}")
            md.append(f"**Type:** {event_type}\n")
            if event.get('rationale'):
                md.append(f"**Rationale:** {event['rationale']}\n")
            if event.get('alternatives'):
                md.append(f"**Alternatives Considered:** {event['alternatives']}\n")
            if event.get('tradeoffs'):
                md.append(f"**Trade-offs:** {event['tradeoffs']}\n")
            md.append("")
        
        return '\n'.join(md)
    
    def _generate_implementation_md(self, aar_data: Dict) -> str:
        """Generate IMPLEMENTATION.md - Technical details"""
        thread_id = self.thread_id
        export_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        artifacts = aar_data.get('final_state', {}).get('artifacts', [])
        outcome = self._get_outcome(aar_data)
        
        md = []
        md.append(f"# Technical Implementation")
        md.append(f"\n**Thread ID:** {thread_id}  ")
        md.append(f"**Date:** {export_date}  ")
        md.append(f"\n---\n")
        
        md.append("## What Was Completed\n")
        md.append(f"{outcome}\n")
        
        md.append("## File Structure\n")
        if artifacts:
            by_type = self._get_artifacts_by_type(artifacts)
            for atype in sorted(by_type.keys()):
                items = by_type[atype]
                md.append(f"### {atype.capitalize()} Files\n")
                for item in items[:MAX_FILES_IN_TREE]:
                    size = self._format_file_size(item['size_bytes'])
                    md.append(f"- **`{item['filename']}`** ({size})")
                    if item.get('description'):
                        md.append(f"  - {item['description']}")
                if len(items) > MAX_FILES_IN_TREE:
                    md.append(f"  *(+{len(items) - MAX_FILES_IN_TREE} more files)*")
                md.append("")
        
        return '\n'.join(md)
    
    def _generate_validation_md(self, aar_data: Dict) -> str:
        """Generate VALIDATION.md - Testing and troubleshooting"""
        thread_id = self.thread_id
        export_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        md = []
        md.append(f"# Validation & Troubleshooting")
        md.append(f"\n**Thread ID:** {thread_id}  ")
        md.append(f"**Date:** {export_date}  ")
        md.append(f"\n---\n")
        
        md.append("## Testing Status\n")
        md.append("*Testing details would be captured during implementation*\n")
        
        md.append("## Known Issues / Gotchas\n")
        md.append("*Issues encountered during work would be documented here*\n")
        
        md.append("## Troubleshooting Guide\n")
        md.append("*Common issues and solutions from the thread*\n")
        
        return '\n'.join(md)
    
    def _generate_context_md(self, aar_data: Dict) -> str:
        """Generate CONTEXT.md - Historical context and metadata"""
        thread_id = self.thread_id
        export_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        title = aar_data.get('title', 'Conversation')
        telemetry = aar_data.get('telemetry', {})
        metadata = aar_data.get('metadata', {})
        
        md = []
        md.append(f"# Thread Context")
        md.append(f"\n**Thread ID:** {thread_id}  ")
        md.append(f"**Title:** {title}  ")
        md.append(f"**Date:** {export_date}  ")
        md.append(f"\n---\n")
        
        md.append("## Thread Lineage\n")
        md.append("*Previous and related threads would be listed here*\n")
        
        md.append("## Metadata & Telemetry\n")
        if telemetry:
            md.append("```json")
            md.append(json.dumps(telemetry, indent=2))
            md.append("```\n")
        
        if metadata:
            md.append("### Additional Metadata\n")
            md.append("```json")
            md.append(json.dumps(metadata, indent=2))
            md.append("```")
        
        return '\n'.join(md)
    
    def save_modular_aar(self, aar_data: Dict, next_thread_title: Optional[str] = None):
        """Save AAR in modular format (v2.2) with atomic writes"""
        import tempfile
        
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Write JSON (source of truth)
            if not self.dry_run:
                with open(self.aar_json_path, 'w', encoding='utf-8') as f:
                    json.dump(aar_data, f, indent=2, ensure_ascii=False)
            print(f"  {'[DRY-RUN]' if self.dry_run else '✓'} Saved JSON: {self.aar_json_path.name}")
            
            # Generate modular markdown files
            modular_exports = self.generate_modular_exports(aar_data)
            
            # Write markdown files atomically
            for filename, content in modular_exports.items():
                file_path = self.archive_dir / filename
                if not self.dry_run:
                    with tempfile.NamedTemporaryFile('w', encoding='utf-8',
                                                    dir=file_path.parent,
                                                    delete=False) as tmp:
                        tmp.write(content)
                        tmp_path = Path(tmp.name)
                    tmp_path.rename(file_path)
                print(f"  {'[DRY-RUN]' if self.dry_run else '✓'} Saved: {filename}")
        
        except IOError as e:
            print(f"  ❌ Error writing files: {e}")
            raise
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            raise
    
    def save_aar(self, aar_data: Dict, markdown: str):
        """Save AAR in both JSON and Markdown formats (dual-write)"""
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Write JSON (source of truth)
        if not self.dry_run:
            with open(self.aar_json_path, 'w', encoding='utf-8') as f:
                json.dump(aar_data, f, indent=2, ensure_ascii=False)
        print(f"  {'[DRY-RUN]' if self.dry_run else '✓'} Saved JSON: {self.aar_json_path}")
        
        # Write Markdown (generated view)
        if not self.dry_run:
            with open(self.aar_md_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
        print(f"  {'[DRY-RUN]' if self.dry_run else '✓'} Saved Markdown: {self.aar_md_path}")
    
    def run(self, interactive=True, export_format='modular'):
        """Execute full AAR export workflow
        
        Args:
            interactive: Whether to use interactive mode
            export_format: 'single' for v2.0 format, 'modular' for v2.2 format
        """
        
        print("\n" + "="*70)
        print(f"Thread Export: {self.thread_id}")
        print("="*70)
        
        # Inventory artifacts
        print("\nPhase 1: Inventory Artifacts")
        self.discover_artifacts()
        print(f"  Found {len(self.artifacts)} artifacts in conversation workspace")
        
        # Detect conversation type for smart extraction
        if not interactive:
            conv_type = self.detect_conversation_type()
            print(f"  Detected conversation type: {conv_type}")
        
        # Generate AAR data
        if interactive:
            print("\nPhase 2: Interactive AAR Generation")
            self.aar_data = self.generate_interactive_aar()
        else:
            print("\nPhase 2: Smart AAR Generation (Content Extraction)")
            if self.dry_run:
                print("  [DRY-RUN] Preview mode - using smart extraction")
            self.aar_data = self.generate_smart_aar()
        
        # Generate next thread title (if generator available and we have a current title)
        next_thread_title = None
        if TITLE_GENERATOR_AVAILABLE and self.title:
            try:
                title_generator = TitleGenerator()
                next_thread_title = title_generator.generate_next_thread_title(self.title)
                if next_thread_title:
                    print(f"\n  📝 Generated next thread title: {next_thread_title}")
            except Exception as e:
                print(f"  ⚠️  Could not generate next thread title: {e}")
        
        print("\nPhase 3: Validate AAR Data")
        valid, errors = self.validate_aar(self.aar_data)
        if not valid:
            print("  ⚠️  Validation warnings:")
            for error in errors:
                print(f"    {error}")
        else:
            print("  ✓ AAR validated against schema")
        
        markdown = self.generate_markdown(self.aar_data)
        
        # Preview
        print("\nPhase 4: Archive Structure")
        print(f"  Archive directory: {self.archive_dir}")
        print(f"  AAR JSON: {self.aar_json_path.name}")
        print(f"  AAR Markdown: {self.aar_md_path.name}")
        print(f"  Artifacts: {len(self.artifacts)} files → artifacts/")
        
        # Dry-run check
        if self.dry_run:
            print("\n[DRY-RUN MODE] - No files will be written")
            print("\nPhase 6: Timeline Check")
            if TIMELINE_AVAILABLE:
                print("  [DRY-RUN] Timeline detection would analyze AAR for timeline-worthy changes")
            else:
                print("  [DRY-RUN] Timeline module not available")
            print("\nAAR Preview (first 1000 chars):")
            print("-" * 70)
            print(markdown[:1000])
            print("-" * 70)
            return True
        
        # Confirm (unless auto-confirmed)
        if not self.auto_confirm:
            print("\nReady to create archive. Proceed? (y/n): ", end='')
            if input().lower() != 'y':
                print("Cancelled.")
                return False
        
        # Execute
        print("\nPhase 5: Create Archive")
        if export_format == 'modular':
            self.save_modular_aar(self.aar_data, next_thread_title)
        else:
            self.save_aar(self.aar_data, markdown)
        self.copy_artifacts()
        
        # Phase 6: Timeline Integration (if available)
        if TIMELINE_AVAILABLE:
            print("\nPhase 6: Timeline Check")
            try:
                timeline_added = add_timeline_entry_from_aar(self.aar_data)
                if not timeline_added:
                    print("  → No timeline entry created")
            except Exception as e:
                print(f"  ⚠️  Timeline check failed: {e}")
                print("  → Continuing without timeline update")
        
        print(f"\n✅ AAR Export Complete!")
        print(f"   Archive: {self.archive_dir}")
        print(f"   Format: {export_format} (v{AAR_VERSION})")
        
        # Display next thread title prominently
        if next_thread_title:
            print("\n" + "="*70)
            print("🔗 NEXT THREAD TITLE (Copy & Paste)")
            print("="*70)
            print(f"\n{next_thread_title}\n")
            print("When resuming work in a new thread, use this title to maintain")
            print("sequential numbering and thread linkage.")
            print("="*70)
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate After-Action Report (AAR) for conversation threads",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "thread_id",
        nargs='?',
        help="Thread ID (e.g., con_mZrkGmXndDPiWtMR)"
    )
    parser.add_argument(
        "--title",
        help="Descriptive title for the thread (used in archive directory name)"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-detect current thread from most recently modified workspace"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without creating files"
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Skip interactive questions (use artifact data only)"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Auto-confirm all prompts (for automated execution)"
    )
    parser.add_argument(
        "--format",
        choices=["single", "modular"],
        default="modular",
        help="Export format: single file (v2.0) or modular (v2.2, default)"
    )
    
    args = parser.parse_args()
    
    # Determine thread ID
    thread_id = args.thread_id
    if args.auto or not thread_id:
        print("Auto-detecting current thread...")
        exporter = ThreadExporter("dummy")
        thread_id = exporter.detect_thread_id()
        if not thread_id:
            print("❌ Could not detect thread ID. Please specify manually.")
            sys.exit(1)
        print(f"  Detected: {thread_id}")
    
    # Validate thread ID format
    if not thread_id.startswith("con_") or len(thread_id) != 20:
        print(f"❌ Invalid thread ID format: {thread_id}")
        print("   Expected: con_[16 characters]")
        sys.exit(1)
    
    # Title generation workflow
    title = args.title
    
    if not title and TITLE_GENERATOR_AVAILABLE and not args.dry_run:
        # Generate title options automatically
        print("\n" + "="*70)
        print("TITLE GENERATION")
        print("="*70)
        print("\nAnalyzing thread content to generate title suggestions...")
        
        # Create temporary exporter to analyze artifacts
        temp_exporter = ThreadExporter(thread_id, "temp", dry_run=True)
        temp_exporter.discover_artifacts()
        recent = temp_exporter.inventory_recent_workspace_artifacts(lookback_hours=6)
        combined_artifacts = temp_exporter.artifacts + recent
        
        # Generate smart AAR for content analysis and inject combined artifacts
        temp_aar = temp_exporter.generate_smart_aar()
        temp_aar["artifacts"] = [
            {"type": a.get("type", "other"), "filename": str(a.get("relative_path", a.get("filename")))}
            for a in combined_artifacts
        ]
        
        # Generate title options
        title_generator = TitleGenerator()
        title_options = title_generator.generate_titles(
            temp_aar,
            combined_artifacts
        )
        
        if title_options and not args.yes:
            # Interactive selection
            title = title_generator.interactive_select(title_options)
            if not title:
                print("❌ Title generation cancelled.")
                sys.exit(1)
        elif title_options and args.yes:
            # Auto-select first option
            title = title_options[0]['title']
            print(f"\n✓ Auto-selected title: {title}")
        else:
            # Fallback to default
            title = f"conversation-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            print(f"\n⚠️  No title options generated. Using: {title}")
    
    elif not title and not args.dry_run and not args.yes:
        # Manual title entry (fallback if title generator unavailable)
        print("\nProvide a descriptive title for this thread:")
        print("(This will be used in the archive directory name)")
        title = input("Title: ").strip()
    
    elif not title and args.yes:
        # Generate default title for automated execution (ONLY if title generator unavailable)
        title = f"conversation-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Run export
    exporter = ThreadExporter(thread_id, title, args.dry_run)
    exporter.auto_confirm = args.yes  # Set auto-confirm flag
    success = exporter.run(
        interactive=not args.non_interactive and not args.yes,
        export_format=args.format
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
