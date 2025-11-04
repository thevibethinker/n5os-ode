#!/usr/bin/env python3
"""Test validator with database integration"""

import sys
sys.path.insert(0, '/home/workspace')

from Intelligence.scripts import block_db, block_validator

# Test 1: Validation without DB
print("=" * 60)
print("TEST 1: Basic Validation (no DB)")
print("=" * 60)

good_content = """# Stakeholder Intelligence

## Key Stakeholders
- John Smith (CEO) - Decision maker
- Jane Doe (VP Engineering) - Technical lead
- Bob Wilson (Product Manager) - Day-to-day contact

## Organizational Context
The team is currently focused on Q4 launch. Engineering is stretched thin
but excited about the partnership opportunity.

## Decision Process
All partnerships require board approval. John has discretionary budget up to $50K.
"""

bad_content = """# Stakeholder Intelligence

## Key Stakeholders
TBD - need to fill this in

## Organizational Context
[Insert details here]
"""

rubric = {
    "required_sections": ["## Key Stakeholders", "## Organizational Context"],
    "min_length": 100,
    "structure_rules": {
        "must_start_with_heading": True
    }
}

print("\nGood Content:")
result = block_validator.validate_block(good_content, rubric, log_to_db=False)
print(f"Valid: {result['valid']}, Score: {result['score']}")

print("\nBad Content:")
result = block_validator.validate_block(bad_content, rubric, log_to_db=False)
print(f"Valid: {result['valid']}, Score: {result['score']}")
print(f"Feedback:\n{result['feedback']}")

# Test 2: Database integration
print("\n" + "=" * 60)
print("TEST 2: Database Integration")
print("=" * 60)

# Create a test generation record
gen_id = block_db.log_generation(
    block_id="B01",
    meeting_id="TEST_001",
    status="pending"
)
print(f"\nCreated generation record: {gen_id}")

# Validate with DB logging
result = block_validator.validate_block(
    content=good_content,
    rubric=rubric,
    generation_id=gen_id,
    block_id="B01",
    log_to_db=True
)
print(f"Validation result: Valid={result['valid']}, Score={result['score']}")

# Check if validation was logged
validations = block_db.get_validation_results(gen_id)
print(f"\nValidation records in DB: {len(validations)}")
if validations:
    v = validations[0]
    print(f"  Status: {v['status']}")
    print(f"  Score: {v['score']}")
    print(f"  Checks: {v['criteria_checked']}")

# Test 3: Load rubric from database
print("\n" + "=" * 60)
print("TEST 3: Load Rubric from Database")
print("=" * 60)

block = block_db.get_block("B01")
print(f"\nBlock B01 validation_rubric: {block['validation_rubric']}")

rubric = block_validator.load_rubric_from_db("B01")
if rubric:
    print(f"Loaded rubric: {rubric}")
else:
    print("No rubric in DB, using default")
    rubric = block_validator.get_default_rubric()
    print(f"Default rubric: {rubric}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETE")
print("=" * 60)
