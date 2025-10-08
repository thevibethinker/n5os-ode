#!/usr/bin/env python3
"""CLI wrapper for pipeline.generate_ticket"""
import argparse, json, sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent))
from pipeline import generate_ticket


def main():
    p = argparse.ArgumentParser(description="Generate a Careerspan ticket from meeting JSON")
    p.add_argument("input", help="Path to meeting JSON file")
    p.add_argument("output", help="Path to save generated ticket JSON")
    args = p.parse_args()

    with open(args.input, "r") as f:
        meeting = json.load(f)
    ticket = generate_ticket(meeting)
    with open(args.output, "w") as f:
        json.dump(ticket, f, indent=2)
    print(f"Ticket {ticket['id']} saved to {args.output}")

if __name__ == "__main__":
    main()
