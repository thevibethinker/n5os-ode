#!/usr/bin/env python3
"""N5 WheresV Wrapper - Routes natural language to LLM worker"""
import sys, subprocess
instruction = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
if not instruction:
    print("Usage: n5 wheresv <instruction>")
    print("Example: n5 wheresv my flight is UA123 tomorrow")
    sys.exit(1)
print(f"📝 {instruction}")
result = subprocess.run(
    ["python3", "/home/workspace/wheresv2-data/scripts/llm_interpreter.py", instruction],
    capture_output=True, text=True
)
print(result.stdout if result.returncode == 0 else result.stderr)
sys.exit(result.returncode)
