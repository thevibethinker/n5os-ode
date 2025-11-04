# B11 - METRICS_SNAPSHOT Generation Prompt

You are generating a METRICS_SNAPSHOT intelligence block.

## Core Principle

Capture any quantitative data shared about their business—growth metrics, usage stats, financial data, operational KPIs.

## Output Structure

### [Metric Category]

**Metric**: [Specific number/stat]  
**Context**: [What they said, timestamp]  
**Time period**: [When this metric applies]  
**Trend**: [Growing/Flat/Declining if mentioned]  
**Why they shared**: [Signal this sends - credibility, pain point, opportunity]

## Categories

- Revenue/Financial
- User/Customer metrics
- Growth rates
- Operational efficiency
- Market share/competitive position
- Team size/hiring

## Extraction Rules

✅ Include: Specific numbers, percentages, growth rates, timelines, comparative data  
❌ Exclude: Vague statements ("doing well"), aspirational goals without current state

## Quality Standards

✅ DO: Note exact figures with context, analyze what metric reveals  
❌ DON'T: Paraphrase numbers, miss the strategic signal

## Edge Cases

**No metrics shared**: Output: "No quantitative metrics discussed."  
**Sensitive data**: Flag: "CONFIDENTIAL - Handle appropriately"
