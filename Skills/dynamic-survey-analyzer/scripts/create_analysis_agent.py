#!/usr/bin/env python3
"""
Creates a scheduled agent for ongoing survey analysis.

Usage:
    python3 create_analysis_agent.py <formId> [--days 30]

This script uses Zo's create_agent API to set up a recurring analysis task
that checks for new submissions and regenerates analysis if needed.
"""

import json
import sys
import argparse
from pathlib import Path
import requests
import os


def check_existing_agent(form_id):
    """Check if an agent already exists for this form."""
    # This would require list_agents functionality
    # For now, we'll check if the agent was already created in meta.json
    meta_path = Path(f"/home/workspace/Datasets/survey-analyses/{form_id}/meta.json")
    
    if meta_path.exists():
        with open(meta_path) as f:
            meta = json.load(f)
        
        if "agent_id" in meta:
            return meta["agent_id"]
    
    return None


def create_scheduled_agent(form_id, days=30):
    """
    Create a scheduled agent for ongoing survey analysis.
    
    Note: This script prepares the agent configuration but does NOT actually
    create the agent. The actual agent creation requires manual confirmation
    to avoid unintended automated task creation.
    """
    
    # Build the agent instruction
    instruction = f"""You are the Survey Analysis Agent for form {form_id}.

Your task is to:
1. Check for new submissions via the Fillout API using the existing client at Skills/dynamic-survey-analyzer/scripts/fillout_client.py
2. If new submissions exist (count > previous), regenerate analysis:
   - Run quantitative analysis using existing scripts
   - Update the dashboard using generate_dashboard.py
   - Update the analysis.md synthesis document
3. Update the meta.json with timestamp and submission count
4. Do NOT send notifications unless there's a significant change (>20% increase in responses)

Form context:
- Form ID: {form_id}
- Previous submission count: Check Datasets/survey-analyses/{form_id}/meta.json

Analysis location:
- Datasets/survey-analyses/{form_id}/

Use the existing tools and scripts - do not create new workflows. Focus on incremental updates based on new data."""
    
    # RRule for daily execution for N days
    rrule = f"FREQ=DAILY;INTERVAL=1;COUNT={days}"
    
    agent_config = {
        "form_id": form_id,
        "rrule": rrule,
        "instruction": instruction,
        "delivery_method": "none",  # No notifications by default
        "days": days
    }
    
    return agent_config


def save_agent_config(form_id, config):
    """Save agent configuration for manual review."""
    output_dir = Path(f"/home/workspace/Datasets/survey-analyses/{form_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config_path = output_dir / "agent_config.json"
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Agent configuration saved to: {config_path}")
    print("\n⚠️  Agent NOT created automatically.")
    print("To create this agent, run:")
    print(f"  python3 {__file__} {form_id} --create")
    print("\nOr review the configuration at:")
    print(f"  {config_path}")
    
    return config_path


def main():
    parser = argparse.ArgumentParser(
        description="Create a scheduled agent for survey analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Prepare agent config (default 30 days)
  python3 create_analysis_agent.py jPQRwpT4nGus
  
  # Prepare config for 60 days
  python3 create_analysis_agent.py jPQRwpT4nGus --days 60
  
  # Actually create the agent (requires confirmation)
  python3 create_analysis_agent.py jPQRwpT4nGus --create
        """
    )
    parser.add_argument("form_id", help="Form ID to monitor")
    parser.add_argument("--days", "-d", type=int, default=30, 
                       help="Number of days to run (default: 30)")
    parser.add_argument("--create", action="store_true",
                       help="Actually create the agent (default: save config only)")
    
    args = parser.parse_args()
    
    # Check for existing agent
    existing_agent_id = check_existing_agent(args.form_id)
    if existing_agent_id:
        print(f"⚠️  Agent already exists for this form: {existing_agent_id}")
        print("To create a new agent, delete the existing one first.")
        return 1
    
    # Create agent configuration
    config = create_scheduled_agent(args.form_id, args.days)
    
    # Save configuration
    config_path = save_agent_config(args.form_id, config)
    
    # If --create flag, attempt to create the agent
    # Note: This requires the Zo API, which isn't available in this script context
    # The actual agent creation should be done via the Zo interface or API
    if args.create:
        print("\nℹ️  To create this agent:")
        print("1. Review the configuration at:", config_path)
        print("2. Use the Zo interface at /?t=agents to create the agent")
        print("3. Copy the instruction from agent_config.json")
        print(f"4. Set the rrule to: {config['rrule']}")
        print("5. Set delivery method to: none (or email for notifications)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
