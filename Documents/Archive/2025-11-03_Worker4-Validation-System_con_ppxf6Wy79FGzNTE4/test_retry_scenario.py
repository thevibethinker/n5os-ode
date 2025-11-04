#!/usr/bin/env python3
"""Test retry scenario with improving content"""

import sys
sys.path.insert(0, '/home/workspace')

from Intelligence.scripts import block_db, block_validator

rubric = {
    "required_sections": ["## Key Stakeholders", "## Organizational Context", "## Next Steps"],
    "min_length": 150,
    "structure_rules": {
        "must_start_with_heading": True,
        "require_bullet_points": True
    }
}

# Attempt 1: Very bad content
attempt1 = """# Stakeholder Intelligence

## Key Stakeholders
TBD

## Organizational Context
[Insert details here]
"""

# Attempt 2: Better but still incomplete
attempt2 = """# Stakeholder Intelligence

## Key Stakeholders
- John Smith (CEO)
- Jane Doe (VP Engineering)

## Organizational Context
The team is focused on Q4 launch...
"""

# Attempt 3: Good content
attempt3 = """# Stakeholder Intelligence

## Key Stakeholders
- John Smith (CEO) - Final decision maker, enthusiastic about partnership
- Jane Doe (VP Engineering) - Technical lead, wants to see proof of concept first
- Bob Wilson (Product Manager) - Day-to-day contact, handles vendor evaluations

## Organizational Context
The engineering team is currently stretched thin preparing for Q4 product launch.
However, they're actively seeking partnerships that can accelerate their roadmap.
Budget has been approved for strategic partnerships this quarter.

## Next Steps
- Send technical documentation to Jane by Friday
- Schedule follow-up demo with Bob next week
- Prepare ROI analysis for John's board presentation
"""

print("=" * 70)
print("RETRY SCENARIO TEST")
print("=" * 70)

meeting_id = "TEST_RETRY_001"

for attempt_num, content in enumerate([attempt1, attempt2, attempt3], 1):
    print(f"\n{'='*70}")
    print(f"ATTEMPT {attempt_num}")
    print('='*70)
    
    # Log generation
    gen_id = block_db.log_generation(
        block_id="B01",
        meeting_id=meeting_id,
        status="pending",
        attempt_number=attempt_num
    )
    
    # Validate
    result = block_validator.validate_block(
        content=content,
        rubric=rubric,
        generation_id=gen_id,
        block_id="B01",
        log_to_db=True
    )
    
    print(f"\nValid: {result['valid']}")
    print(f"Score: {result['score']}/100")
    
    if result['valid']:
        print("\n✓ VALIDATION PASSED - Content accepted")
        block_db.update_generation(gen_id, status="success")
        block_db.update_block_stats("B01", success=True)
        break
    else:
        print(f"\n✗ VALIDATION FAILED")
        print(f"\nFeedback for retry:\n{result['feedback']}")
        block_db.update_generation(
            gen_id, 
            status="failed",
            error_message=result['feedback']
        )
        block_db.update_block_stats("B01", success=False)
        
        if attempt_num < 3:
            print("\n→ Retrying with improvements...")

# Show final stats
print("\n" + "="*70)
print("FINAL STATISTICS")
print("="*70)

block = block_db.get_block("B01")
print(f"\nBlock B01:")
print(f"  Total generations: {block['total_generations']}")
print(f"  Success rate: {block['success_rate']:.1f}%")

generations = block_db.get_generations_for_meeting(meeting_id)
print(f"\nGenerations for {meeting_id}: {len(generations)}")
for gen in generations:
    print(f"  Attempt {gen['attempt_number']}: {gen['status']}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
