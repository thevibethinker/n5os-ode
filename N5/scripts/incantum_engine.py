#!/usr/bin/env python3
"""
N5 Incantum Engine - Prototype

Natural language trigger recognition and execution system for N5 OS.
Matches incantum triggers against command registry and executes confirmed commands.

Usage:
    python incantum_engine.py "incantum: check list system health"
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# N5 Paths
N5_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_FILE = N5_ROOT / "schemas" / "incantum_triggers.json"
SCRIPTS_DIR = N5_ROOT / "scripts"

class IncantumEngine:
    """Prototype incantum trigger recognition and execution engine."""

    def __init__(self):
        self.triggers = self._load_triggers()
        self.destructive_commands = {
            "index-rebuild",  # Modifies critical files
            "system-upgrades-add",  # Creates system alerts
            # Add more as needed
        }

    def _load_triggers(self) -> Dict:
        """Load trigger registry from JSON file."""
        if not REGISTRY_FILE.exists():
            print("❌ Incantum registry not found")
            return {}

        try:
            with REGISTRY_FILE.open('r', encoding='utf-8') as f:
                data = json.load(f)
            return {trigger['primary_trigger']: trigger for trigger in data.get('triggers', [])}
        except Exception as e:
            print(f"❌ Error loading registry: {e}")
            return {}

    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching: lowercase, remove extra spaces."""
        return re.sub(r'\s+', ' ', text.strip().lower())

    def _calculate_similarity(self, input_text: str, trigger_phrase: str) -> float:
        """Calculate similarity score between input and trigger phrase."""
        input_words = set(self._normalize_text(input_text).split())
        trigger_words = set(self._normalize_text(trigger_phrase).split())

        if not input_words or not trigger_words:
            return 0.0

        # Jaccard similarity: intersection over union
        intersection = len(input_words & trigger_words)
        union = len(input_words | trigger_words)

        return intersection / union if union > 0 else 0.0

    def _find_best_match(self, input_phrase: str) -> Tuple[Optional[Dict], float]:
        """Find the best matching trigger for the input phrase."""
        best_match = None
        best_score = 0.0

        for primary_trigger, trigger_data in self.triggers.items():
            # Check primary trigger
            score = self._calculate_similarity(input_phrase, primary_trigger)
            if score > best_score:
                best_score = score
                best_match = trigger_data

            # Check aliases
            for alias in trigger_data.get('aliases', []):
                score = self._calculate_similarity(input_phrase, alias)
                if score > best_score:
                    best_score = score
                    best_match = trigger_data

        return best_match, best_score

    def _is_destructive(self, command: str) -> bool:
        """Check if command is destructive and requires confirmation."""
        return command in self.destructive_commands

    def _execute_command(self, command: str) -> Tuple[bool, str]:
        """Execute the matched N5 command."""
        # Try different naming conventions
        script_variants = [
            SCRIPTS_DIR / f"n5_{command}.py",
            SCRIPTS_DIR / f"n5_{command.replace('-', '_')}.py",
            SCRIPTS_DIR / f"{command}.py",
            SCRIPTS_DIR / f"{command.replace('-', '_')}.py"
        ]
        
        script_path = None
        for variant in script_variants:
            if variant.exists():
                script_path = variant
                break
        
        if not script_path:
            return False, f"Command script not found. Tried: {[str(v) for v in script_variants]}"

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            success = result.returncode == 0
            output = result.stdout + result.stderr

            return success, output

        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, f"Execution error: {e}"

    def process_incantum(self, user_input: str) -> str:
        """Process an incantum trigger and return response."""
        # Extract incantum phrase
        incantum_pattern = r'^incantum:\s*(.+)$'
        match = re.match(incantum_pattern, user_input, re.IGNORECASE)

        if not match:
            return "❌ Not an incantum trigger. Use format: 'incantum: [action]'"

        trigger_phrase = match.group(1).strip()

        # Find best match
        trigger_data, confidence = self._find_best_match(trigger_phrase)

        if not trigger_data:
            return "❌ No matching incantum trigger found. Try 'incantum: help' for available triggers."

        command = trigger_data['command']
        threshold = trigger_data.get('confidence_threshold', 0.8)

        # Check confidence and destructive nature
        is_destructive = self._is_destructive(command)

        if confidence >= threshold and not is_destructive:
            # High confidence, safe command - execute immediately
            success, output = self._execute_command(command)

            response = f"🪄 Incantum Cast: \"{trigger_phrase}\"\n"
            response += f"Matched: {command} (confidence: {confidence:.2f})\n\n"

            if success:
                response += f"✅ Success\n{output}"
            else:
                response += f"❌ Failed\n{output}"

            return response

        elif confidence >= 0.6:
            # Medium confidence or destructive - ask for confirmation
            confirm_message = f"🪄 Did you mean: \"{trigger_data['primary_trigger']}\" ({command})? [Y/n]\n"
            confirm_message += f"Confidence: {confidence:.2f}\n"
            confirm_message += f"Description: {trigger_data['description']}\n\n"
            confirm_message += "Reply with 'y' to confirm execution."

            # In a real implementation, this would wait for user response
            # For now, we'll simulate the confirmation process
            return confirm_message

        else:
            # Low confidence - suggest alternatives
            response = f"❌ Low confidence match ({confidence:.2f}). Did you mean one of these?\n\n"

            # Show similar triggers
            for primary, data in list(self.triggers.items())[:3]:
                response += f"- {primary} ({data['command']})\n"

            response += "\nTry rephrasing or use 'incantum: help' for all triggers."
            return response

def main():
    """CLI interface for testing incantum engine."""
    if len(sys.argv) < 2:
        print("Usage: python incantum_engine.py \"incantum: [trigger phrase]\"")
        sys.exit(1)

    user_input = sys.argv[1]
    engine = IncantumEngine()
    response = engine.process_incantum(user_input)
    print(response)

if __name__ == "__main__":
    main()