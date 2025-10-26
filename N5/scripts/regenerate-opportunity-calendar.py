#!/usr/bin/env python3
"""
Regenerate the opportunity calendar markdown from the JSONL data.
"""

import json
from datetime import datetime
from pathlib import Path

def generate_markdown():
    calendar_file = Path("/home/workspace/Lists/opportunity-calendar.jsonl")

    opportunities = []
    if calendar_file.exists():
        with open(calendar_file, 'r') as f:
            for line in f:
                if line.strip():
                    opportunities.append(json.loads(line))

    # Sort by priority and deadline
    priority_order = {"high": 0, "medium": 1, "low-medium": 2, "low": 3}
    opportunities.sort(key=lambda x: (
        priority_order.get(x.get("priority", "medium"), 1),
        x.get("deadline") or "9999-99-99"
    ))

    # Separate time-sensitive from ongoing
    time_sensitive = [opp for opp in opportunities if opp.get("deadline")]
    ongoing = [opp for opp in opportunities if not opp.get("deadline")]

    markdown = "# Opportunity Calendar\n\n"
    markdown += "Internal calendar tracking funding opportunities, partnerships, events, and other business development opportunities for Careerspan.\n\n"

    if time_sensitive:
        markdown += "## 📅 Upcoming Deadlines\n\n"
        markdown += "| Deadline | Opportunity | Organization | Type | Stage | Status | Priority | Careerspan Fit |\n"
        markdown += "|----------|-------------|--------------|------|--------|--------|----------|----------------|\n"

        for opp in time_sensitive:
            deadline = opp.get("deadline", "TBD")
            title = opp.get("title", "")
            org = opp.get("organization", "")
            opp_type = opp.get("type", "")
            stage = opp.get("stage", "")
            status = opp.get("status", "")
            priority = opp.get("priority", "")
            fit = opp.get("careerspan_fit", "")
            markdown += f"| {deadline} | {title} | {org} | {opp_type} | {stage} | {status} | {priority} | {fit} |\n"

        markdown += "\n"

    if ongoing:
        markdown += "## 🔄 Ongoing Opportunities\n\n"
        markdown += "| Opportunity | Organization | Type | Stage | Status | Priority | Careerspan Fit |\n"
        markdown += "|-------------|--------------|------|--------|--------|----------|----------------|\n"

        for opp in ongoing:
            title = opp.get("title", "")
            org = opp.get("organization", "")
            opp_type = opp.get("type", "")
            stage = opp.get("stage", "")
            status = opp.get("status", "")
            priority = opp.get("priority", "")
            fit = opp.get("careerspan_fit", "")
            markdown += f"| {title} | {org} | {opp_type} | {stage} | {status} | {priority} | {fit} |\n"

        markdown += "\n"

    # Detailed sections by priority
    markdown += "## 📋 Opportunity Details\n\n"

    priorities = {"high": "🔴 High Priority", "medium": "🟡 Medium Priority", "low-medium": "🟢 Lower Priority", "low": "⚪ Low Priority"}

    for priority_key, section_title in priorities.items():
        section_opps = [opp for opp in opportunities if opp.get("priority") == priority_key]
        if section_opps:
            if priority_key == "high":
                section_title += " - Time-Sensitive" if any(opp.get("deadline") for opp in section_opps) else ""
            markdown += f"### {section_title}\n\n"

            for opp in section_opps:
                markdown += f"#### {opp.get('title', '')}\n"
                if opp.get("deadline"):
                    markdown += f"- **Deadline:** {opp.get('deadline')}\n"
                else:
                    markdown += "- **Deadline:** Rolling applications\n"
                markdown += f"- **Description:** {opp.get('description', '')}\n"
                if opp.get("application_method"):
                    markdown += f"- **Application:** {opp.get('application_method')}\n"
                if opp.get("source"):
                    source_text = f"[{opp.get('source')}]({opp.get('source_url')})" if opp.get("source_url") else opp.get("source")
                    markdown += f"- **Source:** {source_text}\n"
                if opp.get("careerspan_fit"):
                    markdown += f"- **Fit for Careerspan:** {opp.get('careerspan_fit').title()}\n"
                markdown += "\n"

    markdown += "## 📊 Status Legend\n\n"
    markdown += "- **🔴 Active + Time-Sensitive:** High priority, upcoming deadline\n"
    markdown += "- **🟡 Active:** Medium priority, rolling deadlines\n"
    markdown += "- **🟢 Monitoring:** Low priority or not yet relevant\n"
    markdown += "- **⚪ Applied:** Application submitted\n"
    markdown += "- **✅ Won:** Successfully secured opportunity\n"
    markdown += "- **❌ Passed:** Missed deadline or declined\n\n"

    markdown += "## 🔄 Future Automation\n\n"
    markdown += "Once email routing is set up, this calendar will be automatically updated from:\n"
    markdown += "- Funding opportunity emails\n"
    markdown += "- Partnership inquiries\n"
    markdown += "- Event invitations\n"
    markdown += "- Network introductions\n"
    markdown += "- Application deadlines\n"
    markdown += "- Follow-up reminders\n\n"

    markdown += "*Last updated: " + datetime.now().strftime("%Y-%m-%d") + "*"

    # Write to file
    md_file = Path("/home/workspace/Lists/opportunity-calendar.md")
    with open(md_file, 'w') as f:
        f.write(markdown)

    print(f"✓ Regenerated opportunity calendar with {len(opportunities)} opportunities")

if __name__ == "__main__":
    generate_markdown()