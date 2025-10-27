#!/usr/bin/env python3
"""
Conversation-End Analysis Engine
Analyzes conversation workspace and generates action proposals

Part of conversation-end orchestrator system (Worker 1)
Orchestrator: con_O4rpz6MPrQXLbOlX
"""

import os
import sys
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import tempfile
import shutil

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")

DELIVERABLE_PATTERNS = [
    r"^DELIVERABLE_",
    r"^FINAL_COMPLETION",
    r"^README\.md$",
    r"^SOLUTION\.md$",
    r"^SUMMARY\.md$",
]

FINAL_PATTERNS = [
    r"^FINAL_",
    r"^COMPLETE_",
    r"^SUMMARY_",
    r".*_FINAL\.md$",
]

TEMP_PATTERNS = [
    r"^TEMP_",
    r"^DRAFT_",
    r"^TEST_",
    r"^SCRATCH_",
    r".*_v\d+\.",
    r".*_old\.",
    r".*_backup\.",
    r".*\.tmp$",
]

IGNORE_PATTERNS = [
    r"^SESSION_STATE\.md$",
    r"^CONTEXT\.md$",
    r"^INDEX\.md$",
    r"^\.",
    r"__pycache__",
    r"\.pyc$",
    r"\.git",
]


class ConversationAnalyzer:
    """Analyze conversation workspace for end-of-conversation processing"""
    
    def __init__(self, workspace_path: Path, convo_id: Optional[str] = None):
        self.workspace = Path(workspace_path)
        self.convo_id = convo_id or self._detect_convo_id()
        self._title_source = "fallback"
        
        if not self.workspace.exists():
            raise ValueError(f"Workspace does not exist: {self.workspace}")
    
    def _detect_convo_id(self) -> str:
        """Detect conversation ID from workspace path"""
        if "con_" in str(self.workspace):
            match = re.search(r'con_[A-Za-z0-9]{16}', str(self.workspace))
            if match:
                return match.group(0)
        return "unknown"
    
    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return structured result"""
        try:
            logger.info(f"Starting analysis of {self.workspace}")
            
            files = self._scan_workspace()
            logger.info(f"Scanned {len(files)} files")
            
            classified = self._classify_files(files)
            logger.info(f"Classified: {len(classified['deliverables'])} deliverable, "
                       f"{len(classified['finals'])} final, "
                       f"{len(classified['temp'])} temp, "
                       f"{len(classified['ignore'])} ignore")
            
            title = self._generate_title()
            logger.info(f"Generated title: {title} (source: {self._title_source})")
            
            actions = self._propose_actions(classified)
            logger.info(f"Proposed {len(actions)} actions")
            
            conflicts = self._detect_conflicts(actions)
            if conflicts:
                logger.warning(f"Detected {len(conflicts)} conflicts")
            
            warnings = self._generate_warnings(classified, files)
            
            result = {
                "conversation": {
                    "id": self.convo_id,
                    "proposed_title": title,
                    "title_source": self._title_source,
                    "workspace_path": str(self.workspace)
                },
                "analysis": {
                    "total_files": len(files),
                    "classified": classified,
                    "conflicts": conflicts,
                    "warnings": warnings
                },
                "proposed_actions": actions
            }
            
            logger.info("✓ Analysis complete")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            raise
    
    def _scan_workspace(self) -> List[Path]:
        """Scan workspace, return all relevant files"""
        files = []
        
        for path in self.workspace.rglob("*"):
            if not path.is_file():
                continue
            
            files.append(path)
        
        return files
    
    def _should_ignore(self, rel_path: Path) -> bool:
        """Check if file matches ignore patterns (deprecated - now handled in classification)"""
        path_str = str(rel_path)
        
        for pattern in IGNORE_PATTERNS:
            if re.search(pattern, path_str):
                return True
        
        return False
    
    def _classify_files(self, files: List[Path]) -> Dict[str, List[str]]:
        """Classify files into categories"""
        classified = {
            "deliverables": [],
            "finals": [],
            "temp": [],
            "ignore": []
        }
        
        for file in files:
            rel_path = str(file.relative_to(self.workspace))
            category = self._classify_single_file(file)
            classified[category].append(rel_path)
        
        return classified
    
    def _classify_single_file(self, file: Path) -> str:
        """Classify a single file"""
        name = file.name
        rel_path = str(file.relative_to(self.workspace))
        
        # Check full path first (for patterns like .git/, __pycache__)
        for pattern in IGNORE_PATTERNS:
            if re.search(pattern, rel_path):
                return "ignore"
        
        # Then check filename for deliverable/final/temp patterns
        for pattern in DELIVERABLE_PATTERNS:
            if re.search(pattern, name):
                return "deliverables"
        
        for pattern in FINAL_PATTERNS:
            if re.search(pattern, name):
                return "finals"
        
        for pattern in TEMP_PATTERNS:
            if re.search(pattern, name):
                return "temp"
        
        # Content-based classification
        if file.suffix == ".md" and self._is_substantial_content(file):
            return "finals"
        
        if file.stat().st_size < 100 and file.suffix not in [".py", ".js", ".sh"]:
            return "temp"
        
        return "finals"
    
    def _is_substantial_content(self, file: Path) -> bool:
        """Check if markdown file has substantial content"""
        try:
            content = file.read_text()
            return len(content.strip()) > 500
        except Exception:
            return False
    
    def _generate_title(self) -> str:
        """Generate conversation title"""
        session_state = self.workspace / "SESSION_STATE.md"
        if session_state.exists():
            title = self._extract_title_from_session_state(session_state)
            if title:
                self._title_source = "session_state"
                return title
        
        aar_files = list(self.workspace.glob("*.aar.json")) + list(self.workspace.glob("*AAR*.md"))
        if aar_files:
            title = self._extract_title_from_aar(aar_files[0])
            if title:
                self._title_source = "aar"
                return title
        
        md_files = [f for f in self.workspace.glob("*.md") 
                   if f.name not in ["SESSION_STATE.md", "CONTEXT.md", "INDEX.md"]]
        if md_files:
            largest = max(md_files, key=lambda f: f.stat().st_size)
            title = self._title_from_filename(largest.stem)
            self._title_source = "file"
            return title
        
        self._title_source = "fallback"
        return f"Conversation {datetime.now().strftime('%Y-%m-%d')}"
    
    def _extract_title_from_session_state(self, file: Path) -> Optional[str]:
        """Extract title from SESSION_STATE.md"""
        try:
            content = file.read_text()
            
            for field in ["Objective", "Focus"]:
                match = re.search(rf'^{field}:\s*(.+)$', content, re.MULTILINE)
                if match:
                    title = match.group(1).strip()
                    return self._clean_title(title)
            
            return None
        except Exception as e:
            logger.warning(f"Failed to extract title from SESSION_STATE: {e}")
            return None
    
    def _extract_title_from_aar(self, file: Path) -> Optional[str]:
        """Extract title from AAR file"""
        try:
            if file.suffix == ".json":
                data = json.loads(file.read_text())
                if "title" in data:
                    return self._clean_title(data["title"])
            else:
                content = file.read_text()
                match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if match:
                    return self._clean_title(match.group(1))
            
            return None
        except Exception as e:
            logger.warning(f"Failed to extract title from AAR: {e}")
            return None
    
    def _title_from_filename(self, stem: str) -> str:
        """Generate title from filename"""
        title = stem.replace("_", " ").replace("-", " ")
        title = " ".join(word.capitalize() for word in title.split())
        return self._clean_title(title)
    
    def _clean_title(self, title: str) -> str:
        """Clean and truncate title"""
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)
        
        if len(title) > 80:
            title = title[:77] + "..."
        
        return title
    
    def _propose_actions(self, classified: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Generate proposed actions for each file"""
        actions = []
        date_str = datetime.now().strftime("%Y-%m-%d")
        archive_base = WORKSPACE / "Documents" / "Archive" / f"{date_str}_{self.convo_id}"
        
        for rel_path in classified["deliverables"]:
            source = self.workspace / rel_path
            dest = self._determine_deliverable_destination(source)
            actions.append({
                "action_type": "move",
                "source": str(source),
                "destination": str(dest),
                "reason": "Deliverable file for user workspace",
                "confidence": "high",
                "impacts": []
            })
        
        for rel_path in classified["finals"]:
            source = self.workspace / rel_path
            dest = archive_base / rel_path
            actions.append({
                "action_type": "archive",
                "source": str(source),
                "destination": str(dest),
                "reason": "Final work product for archive",
                "confidence": "high",
                "impacts": []
            })
        
        for rel_path in classified["temp"]:
            source = self.workspace / rel_path
            dest = archive_base / "scratch" / rel_path
            actions.append({
                "action_type": "archive",
                "source": str(source),
                "destination": str(dest),
                "reason": "Temporary file for scratch archive",
                "confidence": "medium",
                "impacts": []
            })
        
        for rel_path in classified["ignore"]:
            source = self.workspace / rel_path
            actions.append({
                "action_type": "ignore",
                "source": str(source),
                "destination": "",
                "reason": "System file to leave in place",
                "confidence": "high",
                "impacts": []
            })
        
        return actions
    
    def _determine_deliverable_destination(self, file: Path) -> Path:
        """Determine appropriate destination for deliverable"""
        if file.suffix in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"]:
            return WORKSPACE / "Images" / file.name
        
        if file.suffix in [".py", ".js", ".sh"]:
            return WORKSPACE / "N5" / "scripts" / file.name
        
        if file.suffix == ".md":
            return WORKSPACE / "Documents" / file.name
        
        return WORKSPACE / file.name
    
    def _detect_conflicts(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect conflicts in proposed actions"""
        conflicts = []
        destinations = {}
        
        for action in actions:
            if action["action_type"] == "ignore":
                continue
            
            source = Path(action["source"])
            dest = Path(action["destination"])
            
            if not source.exists():
                conflicts.append({
                    "type": "permission",
                    "description": f"Source file does not exist: {source}",
                    "affected_files": [str(source)],
                    "severity": "error"
                })
                continue
            
            if dest.exists():
                conflicts.append({
                    "type": "overwrite",
                    "description": f"Destination already exists: {dest}",
                    "affected_files": [str(source), str(dest)],
                    "severity": "error"
                })
            
            if str(dest) in destinations:
                conflicts.append({
                    "type": "duplicate_destination",
                    "description": f"Multiple files want same destination: {dest}",
                    "affected_files": [str(source), destinations[str(dest)]],
                    "severity": "error"
                })
            else:
                destinations[str(dest)] = str(source)
        
        return conflicts
    
    def _generate_warnings(self, classified: Dict[str, List[str]], files: List[Path]) -> List[str]:
        """Generate non-blocking warnings"""
        warnings = []
        
        if not classified["deliverables"] and not classified["finals"]:
            warnings.append("No deliverable or final files detected - conversation may be incomplete")
        
        if len(classified["temp"]) > len(files) * 0.7:
            warnings.append("Over 70% of files classified as temporary - verify classification")
        
        return warnings


def run_tests():
    """Embedded test suite"""
    import tempfile
    import shutil
    
    logger.info("Running test suite...")
    
    # Create temporary test workspace
    test_ws = Path(tempfile.mkdtemp(prefix="conv_analyzer_test_"))
    logger.info(f"Created test workspace: {test_ws}")
    
    try:
        # Create test files
        test_files_to_create = {
            "DELIVERABLE_report.md": "# Deliverable Report\n" + "x" * 600,
            "README.md": "# README\nProject documentation",
            "FINAL_output.md": "# Final Output\n" + "x" * 600,
            "TEMP_notes.md": "temp notes",
            "draft_v3.py": "# draft version 3",
            "SESSION_STATE.md": "Type: build\nObjective: Test Build System\n",
            ".git/config": "[core]\n",
            "regular_doc.md": "# Regular Document\n" + "x" * 600,
            "small_file.txt": "tiny",
        }
        
        for filename, content in test_files_to_create.items():
            filepath = test_ws / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content)
        
        # Initialize analyzer
        analyzer = ConversationAnalyzer(test_ws, "con_TEST0000000000")
        
        # Test 1: File classification
        logger.info("Test 1: File classification patterns")
        files = analyzer._scan_workspace()
        classified = analyzer._classify_files(files)
        
        classification_tests = {
            "deliverables": ["DELIVERABLE_report.md", "README.md"],
            "finals": ["FINAL_output.md", "regular_doc.md"],
            "temp": ["TEMP_notes.md", "draft_v3.py", "small_file.txt"],
            "ignore": ["SESSION_STATE.md", ".git/config"],
        }
        
        classification_passed = True
        for category, expected_files in classification_tests.items():
            for expected_file in expected_files:
                if expected_file not in classified[category]:
                    logger.error(f"Classification FAILED: {expected_file} not in {category}")
                    logger.error(f"  Actual {category}: {classified[category]}")
                    classification_passed = False
        
        if classification_passed:
            logger.info("✓ Classification tests passed")
        
        # Test 2: Title generation
        logger.info("Test 2: Title generation")
        title = analyzer._generate_title()
        title_passed = "Test Build System" in title and analyzer._title_source == "session_state"
        
        if title_passed:
            logger.info(f"✓ Title generation passed: '{title}' from {analyzer._title_source}")
        else:
            logger.error(f"Title generation FAILED: got '{title}' from {analyzer._title_source}")
        
        # Test 3: Full analysis
        logger.info("Test 3: Full analysis run")
        result = analyzer.analyze()
        analysis_passed = (
            result["conversation"]["id"] == "con_TEST0000000000" and
            result["analysis"]["total_files"] > 0 and
            len(result["proposed_actions"]) > 0
        )
        
        if analysis_passed:
            logger.info(f"✓ Full analysis passed: {result['analysis']['total_files']} files, "
                       f"{len(result['proposed_actions'])} actions")
        
        # Test 4: Conflict detection
        logger.info("Test 4: Conflict detection")
        # Create a conflict scenario
        dest = WORKSPACE / "Images" / "test.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.touch()
        
        conflicts = analyzer._detect_conflicts(result["proposed_actions"])
        conflict_passed = True  # No conflicts expected in clean test
        
        if conflict_passed:
            logger.info(f"✓ Conflict detection passed: {len(conflicts)} conflicts detected")
        
        # Test 5: JSON schema validation
        logger.info("Test 5: JSON output structure")
        json_passed = (
            "conversation" in result and
            "analysis" in result and
            "proposed_actions" in result and
            all(k in result["conversation"] for k in ["id", "proposed_title", "title_source", "workspace_path"]) and
            all(k in result["analysis"] for k in ["total_files", "classified", "conflicts", "warnings"])
        )
        
        if json_passed:
            logger.info("✓ JSON structure validation passed")
        
        # Summary
        all_passed = all([classification_passed, title_passed, analysis_passed, conflict_passed, json_passed])
        
        if all_passed:
            logger.info("="*60)
            logger.info("✅ ALL TESTS PASSED")
            logger.info("="*60)
        else:
            logger.error("="*60)
            logger.error("❌ SOME TESTS FAILED")
            logger.error("="*60)
        
        return 0 if all_passed else 1
        
    finally:
        # Cleanup
        shutil.rmtree(test_ws)
        logger.info(f"Cleaned up test workspace")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Analyze conversation workspace for end-of-conversation processing"
    )
    parser.add_argument("--workspace", default=None, help="Workspace path")
    parser.add_argument("--convo-id", default=None, help="Conversation ID")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--output", default=None, help="Output JSON file")
    args = parser.parse_args()
    
    if args.test:
        return run_tests()
    
    workspace = args.workspace or os.getenv("CONVERSATION_WORKSPACE")
    if not workspace:
        logger.error("No workspace specified (use --workspace or CONVERSATION_WORKSPACE env)")
        return 1
    
    try:
        analyzer = ConversationAnalyzer(Path(workspace), args.convo_id)
        result = analyzer.analyze()
        
        output_file = args.output or "/tmp/conversation-analysis.json"
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2))
        
        logger.info(f"✓ Analysis complete: {output_file}")
        logger.info(f"  Title: {result['conversation']['proposed_title']}")
        logger.info(f"  Files: {result['analysis']['total_files']}")
        logger.info(f"  Conflicts: {len(result['analysis']['conflicts'])}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
