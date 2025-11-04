#!/usr/bin/env python3
"""Test router with REAL conversation objectives from database"""

import sys
sys.path.insert(0, '/home/workspace/N5/scripts')
from persona_router import PersonaRouter

# Real messages from conversations.db analysis
real_messages = [
    # Researcher examples (should be >=80%)
    ("Scan sources for meeting transcripts, collect all existing gdrive_ids", "researcher"),
    ("Research the top 10 AI assistants and compare features", "researcher"),
    ("Investigate why the pipeline is failing", "researcher"),
    
    # Builder examples (should be >=80%)
    ("Create a compliant scheduled task that finds newsletter emails", "builder"),
    ("Build a task tracker with SQLite", "builder"),
    ("Set up a daily Gmail scan", "builder"),
    
    # Strategist examples (should be >=80%)
    ("Should we pivot to B2B or stick with B2C?", "strategist"),
    ("Deliver a proof-of-concept scanner and execution plan", "strategist"),
    ("Recommend the best approach for this architecture", "strategist"),
    
    # Teacher examples (should be >=80%)
    ("Explain how async/await works in Python", "teacher"),
    ("Produce a demo outline highlighting Zo capabilities", "teacher"),
    ("Help me understand how the routing system works", "teacher"),
    
    # Debugger examples (should be >=80%)
    ("Debug why my script keeps failing", "debugger"),
    ("Fix the broken API connection", "debugger"),
    ("Troubleshoot this error message", "debugger"),
    
    # Operator examples (default, should NOT switch)
    ("Move files from Inbox to Archive", "operator"),
    ("Run the validation workflow", "operator"),
]

router = PersonaRouter()

correct = 0
total = len(real_messages)

print("Testing Router with Real Conversation Patterns\n")
print("="*70)

for message, expected in real_messages:
    decision = router.analyze(message)
    is_correct = decision.persona_key == expected
    status = "✓" if is_correct else "✗"
    
    if is_correct:
        correct += 1
    
    print(f"\n{status} Message: \"{message[:60]}...\"")
    print(f"  Expected: {expected}")
    print(f"  Got: {decision.persona_key} ({decision.confidence:.0%})")
    print(f"  Should Switch: {decision.should_switch}")
    
    if not is_correct:
        print(f"  ❌ MISMATCH!")

print("\n" + "="*70)
print(f"Accuracy: {correct}/{total} ({correct/total*100:.1f}%)")
print(f"Threshold: 80% confidence")
print(f"\nIssues to address:")
print(f"- Too many below 80% threshold")
print(f"- Need stronger trigger matching")
